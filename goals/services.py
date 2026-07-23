from django.db import transaction
from django.http import HttpResponseRedirect

from goals.models import ProgressEntry, LearningGoals


def create_goal_with_milestone(user, form, formset):
    if not formset.is_valid():
        return None, "Invalid Formset"


    with transaction.atomic():
        goal = form.save(commit=False)
        goal.owner = user
        goal.save()

        formset.instance = goal
        milestones = formset.save(commit=False)

        for position, milestone in enumerate(milestones, start=1):
            milestone.goal = goal
            milestone.position = position
            milestone.save()

    return  goal, "Created"


def update_goal_with_milestones(goal, form, formset):
    if not formset.is_valid():
        return None,'InvalidFormset'

    with transaction.atomic():
        goal = form.save()

        formset.instance = goal
        formset.save()

        position = 1

        for milestone_form in formset.forms:
            cleaned_data = milestone_form.cleaned_data
            if not cleaned_data:
                continue
            if cleaned_data.get('DELETE'):
                continue

            milestone = milestone_form.instance

            if milestone.pk:
                milestone.position = position
                milestone.is_completed = cleaned_data.get('is_completed')
                milestone.save(update_fields=['position', 'is_completed'])
                position += 1

    return goal, "Valid"


def create_progress_entry(user, goal, form):
    if goal.owner != user:
        return None,'NotOwner'

    progress = ProgressEntry.objects.create(
        goal=goal,
        progress_percent=form.cleaned_data.get('progress_percent'),
        note=form.cleaned_data.get('note')
    )

    goal.progress_percent = progress.progress_percent

    if form.cleaned_data.get('progress_percent') == 100:
        goal.status = LearningGoals.Status.COMPLETED
        goal.save(update_fields=['status', 'progress_percent'])
    else:
        goal.save(update_fields=['progress_percent'])
    return progress, "Created"




