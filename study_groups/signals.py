from django.db.models.signals import post_save
from django.dispatch import receiver

from study_groups.models import StudyGroup, GroupMembership


@receiver(post_save, sender=StudyGroup)
def create_owner_membership(sender, instance, created, *args, **kwargs):
    if created:
        GroupMembership.objects.get_or_create(
            group=instance,
            user=instance.owner,
            defaults={
                'role': GroupMembership.Role.OWNER,
                'status': GroupMembership.Status.ACTIVE,
            }
        )