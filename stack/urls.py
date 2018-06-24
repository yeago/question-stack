from django.conf.urls import url
from stack import views

urlpatterns = [
    url('^$', views.home, name="stack_question_home"),
    url('^all/$', views.QuestionList.as_view(), name="stack_question_list"),
    url('^add/$', views.add, name="stack_question_add"),
    url('^preview/$', views.preview, name="stack_question_preview"),
    url('^(?P<slug>[^/]+)/$', views.detail, name="stack_question_detail"),
    url('^(?P<slug>[^/]+)/accepted-answer/(?P<comment>[^/]+)/$', views.accepted_answer, name="stack_accepted_answer"),
]
