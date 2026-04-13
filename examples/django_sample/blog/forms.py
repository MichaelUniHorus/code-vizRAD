"""Forms for blog app."""

from django import forms
from blog.models import Post


class PostForm(forms.ModelForm):
    """Form for creating/editing posts."""

    class Meta:
        model = Post
        fields = ['title', 'content']
