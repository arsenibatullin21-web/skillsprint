from django import forms

from study_groups.models import StudyGroup, GroupMembership


class GroupCreateForm(forms.ModelForm):

    class Meta:
        model = StudyGroup
        fields = ['name', 'description', 'visibility', 'avatar', 'rules', 'topic']


