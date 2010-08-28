from django import template
from django.template.loader import render_to_string
from django.db.models import Count
from django.contrib.comments.templatetags.comments import BaseCommentNode, CommentFormNode

from stack import models as sm

register = template.Library()

class KarmaCommentListNode(BaseCommentNode):
    """Insert a list of comments into the context."""
    def get_context_value_from_queryset(self, context, qs):
	question_pk = self.get_target_ctype_pk(context)
	question = sm.Question.objects.get(pk=question_pk[1])
        return list(qs.exclude(pk=question.comment_id).annotate(Count('karma')))

def get_answer_list(parser, token):
    return KarmaCommentListNode.handle_token(parser, token)

register.tag(get_answer_list)

class RenderCommentStageNode(CommentFormNode):
    """Render the comment strage directly"""

    #@classmethod
    def handle_token(cls, parser, token):
        """Class method to parse render_answer_stage and return a Node."""
        tokens = token.contents.split()
        if tokens[1] != 'for':
            raise template.TemplateSyntaxError("Second argument in %r tag must be 'for'" % tokens[0])

        # {% render_comment_form for obj %}
        if len(tokens) == 3:
            return cls(object_expr=parser.compile_filter(tokens[2]))

        # {% render_comment_form for app.models pk %}
        elif len(tokens) == 4:
            return cls(
                ctype = BaseCommentNode.lookup_content_type(tokens[2], tokens[0]),
                object_pk_expr = parser.compile_filter(tokens[3])
            )
    handle_token = classmethod(handle_token)

    def render(self, context):
        ctype, object_pk = self.get_target_ctype_pk(context)
        if object_pk:
            template_search_list = [
                "stack/answer_stage.html"
            ]
            context.push()
            stagestr = render_to_string(template_search_list, {"object" : self.object_expr.resolve(context)}, context)
            context.pop()
            return stagestr
        else:
            return ''

def render_answer_stage(parser, token):
	return RenderCommentStageNode.handle_token(parser, token)

register.tag(render_answer_stage)
