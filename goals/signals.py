from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from goals.models import ProgressEntry, LearningGoals


@receiver(post_save, sender=ProgressEntry)
def update_goal_progress_after_progress_entry_created(sender, instance, created, *args, **kwargs):
    if created:
        goal = instance.goal
        goal.progress_percent = instance.progress_percent

        if instance.progress_percent == 100:
            goal.status = LearningGoals.Status.COMPLETED
            goal.save(update_fields=['progress_percent', 'status'])
        else:
            goal.save(update_fields=['progress_percent'])

