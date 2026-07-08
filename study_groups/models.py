from django.contrib.auth import get_user_model
from django.db import models
from django.template.context_processors import request
from django.utils.text import slugify


class StudyGroup(models.Model):
    class Visibility(models.TextChoices):
        PUBLIC = 'public', 'Public'
        PRIVATE = 'private', 'Private'

    owner = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE, related_name='study_groups')
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)
    description = models.TextField(max_length=500, null=True, blank=True)
    visibility = models.CharField(choices=Visibility.choices, default=Visibility.PUBLIC)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'study_group'
        ordering = ['-created_at']
        verbose_name = 'Study Group'
        verbose_name_plural = 'Study Groups'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class GroupMembership(models.Model):
    class Role(models.TextChoices):
        OWNER = 'owner', 'Owner'
        MODERATOR = 'moderator', 'Moderator'
        MEMBER = 'member', 'Member'
    group = models.ForeignKey(to=StudyGroup, on_delete=models.CASCADE, related_name='membership')
    user = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE, related_name='membership')
    role = models.CharField(choices=Role.choices, default=Role.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
            fields=['user', 'group'],
            name='unique_user_group'
        )]
        db_table = 'group membership'
        ordering = ['joined_at']
        verbose_name = 'Group Membership'
        verbose_name_plural = 'Group Memberships'

    def __str__(self):
        return f"{self.group} -> {self.user.username} -> {self.joined_at}"









