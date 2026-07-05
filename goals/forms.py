from django import forms
from django.forms.models import inlineformset_factory

from goals.models import LearningGoals, Milestone


class GoalCreateForm(forms.ModelForm):

    class Meta:
        model = LearningGoals
        fields = ['title', 'description', 'visibility', 'status','deadline']


MilestoneFormSet = inlineformset_factory(
    parent_model=LearningGoals,
    model=Milestone,
    fields=["title", "due_date"],
    extra=2,
    can_delete=True,
    widgets={
        "title": forms.TextInput(
            attrs={"placeholder": "Milestone title"}
        ),
        "due_date": forms.DateInput(
            attrs={"type": "date"}
        ),
    },
)
