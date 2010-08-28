from django.conf.urls.defaults import *

urlpatterns = patterns('stack.views',
	url('^add/$','add',name="stack_add"),
	url('^(?P<slug>[^/]+)/$','detail',name="stack_question_detail"),
	url('^(?P<slug>[^/]+)/accepted-answer/(?P<comment>[^/]+)$','accepted_answer',name="stack_accepted_answer"),
)
