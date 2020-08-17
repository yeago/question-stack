from django.db import models
import datetime
from django.template.defaultfilters import slugify
from django.db import IntegrityError
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.conf import settings
import django_comments
from djangoratings.fields import RatingField

Comment = django_comments.get_model()


def SlugifyUniquely(value, model, slugfield="slug"):
    """Returns a slug on a name which is unique within a model's table

    This code suffers a race condition between when a unique
    slug is determined and when the object with that slug is saved.
    It's also not exactly database friendly if there is a high
    likelyhood of common slugs being attempted.

    A good usage pattern for thrandom
    is code would be to add a custom save()
    method to a model with a slug field along the lines of:

    from django.template.defaultfilters import slugify

    def save(self):
    if not self.id:
    # replace self.name with your prepopulate_from field
    self.slug = SlugifyUniquely(self.name, self.__class__)
    super(self.__class__, self).save()

    Original pattern discussed at
    http://www.b-list.org/weblog/2006/11/02/django-tips-auto-populated-fields
    """
    MAX_SUFFIX_LENGTH = getattr(settings, 'MAX_SUFFIX_LENGTH', 3)
    SUFFIX_CHARS = getattr(settings, 'SUFFIX_CHARS', 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
    SLUGIFY_MAX_ATTEMPTS = getattr(settings, 'SLUGIFY_MAX_ATTEMPTS', 250)
    max_length = model._meta.get_field(slugfield).max_length
    potential = base = slugify(value)
    date = datetime.date.today().strftime("%d-%m-%y")

    def random_suffix_generator(size=MAX_SUFFIX_LENGTH, chars=SUFFIX_CHARS):
        """
        Generates a random string of length determined by size and using the
        alphabet indicated by chars.
        """
        return ''.join(random.choice(chars) for i in range(size))
    
    for attempt in xrange(SLUGIFY_MAX_ATTEMPTS):
        old_potential = potential
        random_suffix = random_suffix_generator()
        try:
            # For the first try (0) just use the base
            # For the next 5 tries, just add a number
            if 5 > attempt > 0:
                potential = '%s-%s' % (base[:max_length - 2], attempt)
            # One try with just the date
            if attempt == 5:
                potential = '%s-%s' % (date, base)
            # Everything else failed,
            # use the date plus a random suffix for the rest
            elif attempt > 5:
                potential = '%s-%s-%s' % (date, random_suffix, base)

            # Cut it to the max length of the model slug field.
            potential = potential[:max_length]
            model.objects.get(**{slugfield: potential})

            if attempt > 0 and potential == old_potential:
                # Then, the next iteration will be the same, just stop.
                raise Exception("SlugifyUnique: not able to generate an unique slug. (%s)" % potential)
        except model.DoesNotExist:
            # Good, we found one.
            return potential

    # Oh noo! Max attempts reached.
    raise Exception("SlugifyUnique: Max attempts reached. (%s) last value: %s" % (SLUGIFY_MAX_ATTEMPTS, potential))


class Question(models.Model):
    site = models.ForeignKey('sites.Site', on_delete=models.PROTECT)
    comment = models.OneToOneField(Comment, on_delete=models.CASCADE, null=True)  # Null because it needs to be saved first
    rating = RatingField(can_change_vote=True, allow_anonymous=True, range=1, editable=False)
    title = models.CharField(max_length=250, verbose_name="Question")
    slug = models.CharField(max_length=255)
    views = models.IntegerField(editable=False, default=0, db_column="view_count_cache")
    accepted_answer = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="accepted_answers", null=True, blank=True)
    has_answer = models.BooleanField(default=False)
    closed = models.BooleanField(default=False)

    def __unicode__(self):
        return self.title.replace("[[", "").replace("]]", "")

    def __str__(self):
        return self.title.replace("[[", "").replace("]]", "")

    def get_response_count(self):
        return Comment.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            object_pk=self.pk).count() - 1  # One is the actual question

    def get_absolute_url(self):
        return reverse("stack_question_detail", args=[self.slug])

    def save(self, *args, **kwargs):
        self.site = Site.objects.get_current()
        if not self.slug:
            self.generate_slug()

        if self.accepted_answer_id:
            self.has_answer = True

        while True:
            try:
                super(Question, self).save(*args, **kwargs)
                return
            except IntegrityError:
                self.generate_slug()

    def generate_slug(self):
        length = Question._meta.get_field('title').max_length
        self.title = self.title[:length]
        self.slug = SlugifyUniquely(self.title, Question)
        if not self.slug:
            self.slug = SlugifyUniquely("question", Question)
