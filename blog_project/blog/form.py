from django import forms

class ChooseBlog(forms.Form):
    blog_platform = forms.CharField(max_length=50,required=True,help_text="블로그 플랫폼을 선택하여 주세요")