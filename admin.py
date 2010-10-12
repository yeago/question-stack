from django.contrib import admin
from stack import models as sm

def title_snippet(obj):
	return obj.title[:30]

def user(obj):
	return obj.comment.user


def convert_to_forum(modeladmin,request, qs):
	if not qs:
		return

	from forum.models import Forum, Thread
	from django.contrib.comments.models import Comment
	from django.contrib.contenttypes.models import ContentType
	ct = ContentType.objects.get_for_model(Thread)
	f = Forum.objects.get(title="General")
	for q in qs:
		comments = Comment.objects.for_model(q)
		latest_post = None
		if comments:
			latest_post = list(comments)[-1]
		t = Thread.objects.create(forum=f,title=q.title,latest_post=latest_post)
		comments.update(content_type=ct,object_pk=t.pk)
		q.delete()
		

convert_to_forum.short_description = "Convert to a General forum topic"

class QuestionAdmin(admin.ModelAdmin):
	actions = [convert_to_forum]
	list_display = [title_snippet,user]
	raw_id_fields = ['comment','accepted_answer']

admin.site.register(sm.Question,QuestionAdmin)
