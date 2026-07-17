from django.contrib.auth import get_user_model
from django.db import models

from study_groups.models import GroupPost


# Create your models here.

class Comment(models.Model):
    post = models.ForeignKey(to=GroupPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey(to='self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    context = models.TextField(max_length=500)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        db_table = 'comments'
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'

    def __str__(self):
        return f"{self.author} -> {self.post.title}"

class Reaction(models.Model):
    class Type(models.TextChoices):
        LIKE = 'like', 'Like'
        HELPFUL = 'helpful', 'Helpful'
        CELEBRATE = 'celebrate', 'Celebrate'

    post = models.ForeignKey(to=GroupPost, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE, related_name='reactions')
    type = models.CharField(choices=Type.choices, default=Type.LIKE)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        db_table = 'reaction'
        verbose_name = 'Reaction'
        verbose_name_plural = 'Reactions'
        constraints = [
            models.UniqueConstraint(
                fields=('post', 'user'),
                name='unique_post_user_reaction'
            ),
        ]

class Bookmark(models.Model):
    post = models.ForeignKey(to=GroupPost, on_delete=models.CASCADE, related_name='bookmarks')
    user = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        db_table = 'bookmarks'
        verbose_name = 'Bookmark'
        verbose_name_plural = 'Bookmarks'
        constraints = [
            models.UniqueConstraint(
                fields=['post', 'user'],
                name='unique_post_user_bookmark'
            )
        ]