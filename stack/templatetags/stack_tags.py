from django import template
from django.db.models import Count
from comments_plus.templatetags import comments_plus_tags as tt
from stack import models as sm

register = template.Library()


class KarmaCommentListNode(tt.KarmaCommentListNode):
    """Insert a list of comments into the context."""
    def get_context_value_from_queryset(self, context, qs):
        question_pk = self.get_target_ctype_pk(context)
        question = sm.Question.objects.get(pk=question_pk[1])
        return list(qs.exclude(pk=question.comment_id).annotate(Count('karma')))


def get_answer_list(parser, token):
    return KarmaCommentListNode.handle_token(parser, token)

register.tag(get_answer_list)


@register.simple_tag(takes_context=True)
def render_answer_stage(context, instance, *args, **kwargs):
    kwargs['template'] = "stack/answer_stage.html"
    return tt.render_comment_stage(context, instance, *args, **kwargs)
