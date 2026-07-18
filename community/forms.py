from django import forms

from study_groups.models import GroupPost
from .models import Comment, Reaction


class PostCreateForm(forms.ModelForm):

    class Meta:
        model = GroupPost
        fields = ['title', 'content']

class CommentCreateForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['context']

