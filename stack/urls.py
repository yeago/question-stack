from django.conf.urls.defaults import *

urlpatterns = patterns('stack.views',
	url('^$','question_list',name="stack_question_list"),
	url('^add/$','add',name="stack_question_add"),
	url('^(?P<slug>[^/]+)/$','detail',name="stack_question_detail"),
	url('^(?P<slug>[^/]+)/accepted-answer/(?P<comment>[^/]+)/$','accepted_answer',name="stack_accepted_answer"),
)
