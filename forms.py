from django import forms

from stack import models as sm

class QuestionForm(forms.ModelForm):
	comment = forms.CharField(widget=forms.widgets.Textarea,label="Explanation",help_text="Background about your question")
	def __init__(self,*args,**kwargs):
		super(QuestionForm,self).__init__(*args,**kwargs)
		self.fields['title'].widget.attrs = {'style': 'width:400px;font-size:18px'}

	class Meta:
		model = sm.Question
		exclude = ['comment','slug']
