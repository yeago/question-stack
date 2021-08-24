from datetime import datetime
from django import forms
from django.contrib.admin.models import LogEntry, CHANGE

from django.http import Http404, HttpResponseRedirect, HttpResponseForbidden

from django.views.generic.list import ListView
from django.shortcuts import render, redirect, get_object_or_404

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from django.contrib import messages
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType

import django_comments

from stack import models as sm
from stack import forms as sf

LOGIN_URL = getattr(settings, 'LOGIN_URL', '/accounts/login/')


@login_required(login_url=LOGIN_URL)
def add(request, form_class=sf.QuestionForm):
    form = form_class(request.POST or None, prefix="question")

    return render(request, 'stack/add.html', {'form': form, })


@login_required(login_url=LOGIN_URL)
def preview(request, form_class=sf.QuestionForm):
    """
    Renders a preview of the new question and gives the user
    the option to modify it before sending. If called without
    a POST, redirects to add question.

    Only allows a user to post a question if they're logged in.
    """

    form = form_class(request.POST or None, prefix='question')

    if request.method == "POST" and form.is_valid():
        q = form.instance
        CommentModel = django_comments.get_model()
        user = request.user
        if form.cleaned_data.get('username'):
            user = User.objects.get(username=form.cleaned_data.get('username'))

        ct = ContentType.objects.get_for_model(q)

        if 'preview' in request.POST:
            return render(
                request,
                'stack/preview.html',
                {
                    'form': form,
                    'question': q,
                    'comment': form.cleaned_data['comment'],
                    'user': user,
                    'comment_submit_date': form.cleaned_data.get('date', None) or datetime.now(),
                    'preview_called': True
                })
        else:
            # No preview means we're ready to save the post.
            comment = CommentModel.objects.create(
                comment=form.cleaned_data.get('comment'),
                user=user,
                content_type=ct,
                object_pk=q.pk,
                site=Site.objects.get_current(),
                submit_date=form.cleaned_data.get('date', None) or datetime.now())
            if not comment.pk:
                raise forms.ValidationError("Something went wrong when posting the question, please try again.")
            q.comment = comment
            q.save()
            messages.success(request, "Question posted")

            return HttpResponseRedirect(q.get_absolute_url())
    return render(request, 'stack/preview.html', {'form': form})


def home(request):
    return render(
        request,
        "stack/home.html",
        {"answered": sm.Question.objects.filter(site=settings.SITE_ID, has_answer=True).order_by('-pk'),
         "unanswered": sm.Question.objects.filter(site=settings.SITE_ID, has_answer=False)})


class QuestionList(ListView):
    paginate_by = 20
    def get_queryset(self, **kwargs):
        return sm.Question.objects.filter(site=settings.SITE_ID).select_related(\
            ).order_by('-comment__submit_date')


def detail(request, slug):
    instance = get_object_or_404(sm.Question,slug=slug, site=settings.SITE_ID)
    CommentModel = django_comments.get_model()
    responses = CommentModel.objects.for_model(instance).exclude(pk=instance.comment_id)
    return render(request, "stack/question_detail.html", {'instance': instance, 'responses': responses})


def accepted_answer(request, slug, comment):
    instance = get_object_or_404(sm.Question,slug=slug, site=settings.SITE_ID)

    Comment = django_comments.get_model()
    comment = get_object_or_404(Comment,pk=comment)
    if not instance == comment.content_object:
        raise Http404

    if not request.user.has_perm('stack.change_question') and not request.user == instance.comment.user:
        raise Http404

    if instance.accepted_answer:
        messages.warning(request,"You have changed the accepted answer")
    else:
        messages.success(request,"Answer has been marked as accepted")

    if request.user.has_perm('stack.change_question'):  # Admin therefore adminlog
        LogEntry.objects.log_action(
            request.user.pk,
            ContentType.objects.get_for_model(instance).pk,
            instance.pk,
            '%s' % instance,
            CHANGE,
            "from [%s] to [%s]" % (instance.accepted_answer, comment)
        )
    instance.accepted_answer = comment
    instance.has_answer = True
    instance.save()
    return redirect(instance.get_absolute_url())
