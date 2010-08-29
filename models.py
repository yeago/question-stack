from django.db import models
from django.contrib import comments
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType

from djangoratings.fields import RatingField
from slugify import SlugifyUniquely

Comment = comments.get_model()

class Question(models.Model):
	comment = models.OneToOneField(Comment,null=True) # Null because it needs to be saved first
	rating = RatingField(can_change_vote=True,allow_anonymous=True,range=1,editable=False)
	title = models.CharField(max_length=250,verbose_name="Question")
	slug = models.CharField(max_length=255)
	view_count_cache = models.IntegerField(editable=False,default=0)
	accepted_answer = models.ForeignKey(Comment,related_name="accepted_answers",null=True,blank=True)

	def __unicode__(self):
		return self.title

	def get_response_count(self):
		return Comment.objects.filter(content_type=ContentType.objects.get_for_model(self),object_pk=self.pk).count()

	def get_absolute_url(self):
		return reverse("stack_question_detail",args=[self.slug])

	def save(self,*args,**kwargs):
		if not self.slug:
			self.generate_slug()
		
		from django.db import IntegrityError
		while True:
			try:
				super(Question,self).save(*args,**kwargs)
				return
			except IntegrityError, e:
				self.generate_slug()

	def generate_slug(self):
		length = Question._meta.get_field('title').max_length
		self.title = self.title[:length]
		self.slug = SlugifyUniquely(self.title, Question)
		if not self.slug:
			self.slug = SlugifyUniquely("question", Question)
