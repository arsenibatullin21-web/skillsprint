from django.contrib import admin

from goals.models import LearningGoals, Milestone, ProgressEntry


@admin.register(LearningGoals)
class LearningGoalsAdmin(admin.ModelAdmin):
    list_display = ['status', 'visibility', 'owner', 'title', 'progress_percent']
    search_fields = ['status', 'title', 'visibility']

@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ['goal', 'title', 'is_completed', 'due_date']
    search_fields = ['title', ]

@admin.register(ProgressEntry)
class ProgressEntryModel(admin.ModelAdmin):
    list_display = ['goal', 'progress_percent']
    search_fields = ['note']