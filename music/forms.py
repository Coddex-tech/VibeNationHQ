from django import forms
from .models import MusicComment

class MusicCommentForm(forms.ModelForm):
    class Meta:
        model = MusicComment
        fields = ('name', 'content')
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Write a comment…'
            })
        }
