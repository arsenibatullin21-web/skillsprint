from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from datetime import timedelta

class LearningGoals(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        COMPLETED = 'completed', 'Completed'
        PAUSED = 'paused', 'Paused'
        CANCELED = 'canceled', 'CANCELED'
    class Visibility(models.TextChoices):
        PUBLIC = 'public', 'Public'
        PRIVATE = 'private', 'Private'

    owner = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE, related_name='learning_goals')
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500, blank=True, null=True)
    status = models.CharField(choices=Status.choices, default=Status.ACTIVE)
    visibility = models.CharField(choices=Visibility.choices, default=Visibility.PUBLIC)
    progress_percent = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    deadline = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        db_table = 'learning_goals'
        verbose_name = 'Learning Goal'
        verbose_name_plural = 'Learning Goals'

    def __str__(self):
        return f"{self.title} -> {self.owner}"

    @property
    def remaining_days(self):
        if self.deadline is None:
            return None
        remain = (self.deadline - timezone.localdate()).days
        return remain



class Milestone(models.Model):
    goal = models.ForeignKey(to=LearningGoals, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=50)
    is_completed = models.BooleanField(default=False)
    due_date = models.DateField(null=True, blank=True)
    position = models.PositiveIntegerField(default=0)


    class Meta:
        ordering = ['title']
        db_table = 'milestone'
        verbose_name = 'Milestone'
        verbose_name_plural = 'Milestones'

    def __str__(self):
        return self.title


class ProgressEntry(models.Model):
    goal = models.ForeignKey(to=LearningGoals, on_delete=models.CASCADE, related_name='progress')
    progress_percent = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    note = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        db_table = 'progress_entry'
        verbose_name = "Progress Entry"
        verbose_name_plural = "Progress Entries"

    def __str__(self):
        return str(self.progress_percent)


