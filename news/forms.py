from django import forms
from .models import NewsComment

class NewsCommentForm(forms.ModelForm):
    class Meta:
        model = NewsComment
        fields = ['name', 'content']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Name'
            }),
            
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Write a comment...'
            })
        }
