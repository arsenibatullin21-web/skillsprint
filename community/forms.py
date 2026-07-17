from django import forms

from study_groups.models import GroupPost


class PostCreateForm(forms.ModelForm):

    class Meta:
        model = GroupPost
        fields = ['title', 'content']

