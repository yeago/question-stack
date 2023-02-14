from django.urls import re_path
from stack import views

urlpatterns = [
    re_path('^$', views.home, name="stack_question_home"),
    re_path('^all/$', views.QuestionList.as_view(), name="stack_question_list"),
    re_path('^add/$', views.add, name="stack_question_add"),
    re_path('^preview/$', views.preview, name="stack_question_preview"),
    re_path('^(?P<slug>[^/]+)/$', views.detail, name="stack_question_detail"),
    re_path('^(?P<slug>[^/]+)/accepted-answer/(?P<comment>[^/]+)/$', views.accepted_answer, name="stack_accepted_answer"),
]
