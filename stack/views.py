from datetime import datetime

from django.template import RequestContext
from django.http import Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404

from django.views.generic.list_detail import object_list

from django.contrib import messages
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType

from django.contrib import comments

from stack import models as sm
from stack import forms as sf

def add(request,form_class=sf.QuestionForm):
	form = form_class(request.POST or None,prefix="question")
	if request.POST and form.is_valid():
		instance = form.save()
		CommentModel = comments.get_model()
		user = request.user
		if form.cleaned_data.get('username'):
			user = User.objects.get(username=form.cleaned_data.get('username'))

		ct = ContentType.objects.get_for_model(instance)
		instance.comment = CommentModel.objects.create(\
			comment=form.cleaned_data.get('comment'),
			user=user,
			content_type=ct,
			object_pk=instance.pk,
			site=Site.objects.get_current(),
			submit_date=form.cleaned_data.get('date',None) or datetime.now())

		instance.save()
		messages.success(request,"Question posted")
		return redirect(instance.get_absolute_url())

	return render_to_response("stack/add.html",{'form': form, },\
		context_instance=RequestContext(request))

def home(request):
	return render_to_response("stack/home.html", {"answered": sm.Question.objects.filter(has_answer=True),\
		"unanswered": sm.Question.objects.filter(has_answer=False)},context_instance=RequestContext(request))

def question_list(request):
	return object_list(request,sm.Question.objects.select_related(\
		'accepted_answer','comment').order_by('-comment__submit_date'),\
		paginate_by=20,page=request.GET.get('p') or None)

def detail(request,slug):
	instance = get_object_or_404(sm.Question,slug=slug)
	CommentModel = comments.get_model()
	responses = CommentModel.objects.for_model(instance).exclude(pk=instance.comment_id)
	return render_to_response("stack/question_detail.html",{'instance': instance, 'responses': responses},\
		context_instance=RequestContext(request))

def accepted_answer(request,slug,comment):
	instance = get_object_or_404(sm.Question,slug=slug)

	Comment = comments.get_model()
	comment = get_object_or_404(Comment,pk=comment)
	if not instance == comment.content_object:
		raise Http404

	if not request.user.has_perm('stack.change_question') and not request.user == instance.comment.user:
		raise Http404

	if instance.accepted_answer:
		messages.warning(request,"You have changed the accepted answer")
	else:
		messages.success(request,"Answer has been marked as accepted")

	instance.accepted_answer = comment
	instance.has_answer = True
	instance.save()
	return redirect(instance.get_absolute_url())
