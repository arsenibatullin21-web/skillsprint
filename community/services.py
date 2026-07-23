from django.contrib import messages
from django.shortcuts import redirect

from community.models import Reaction, Bookmark
from study_groups.models import StudyGroup, GroupMembership


def toggle_reaction(user, post, reaction_type, remove=False):
    reaction = Reaction.objects.filter(
        post=post,
        user=user
    ).first()

    if reaction_type not in Reaction.Type.values:
       return None, 'invalid'

    if remove and reaction and reaction.type == reaction_type:
        reaction.delete()
        return None, 'deleted'
    else:
        reaction, created = Reaction.objects.update_or_create(
            post=post,
            user=user,
            defaults={'type': reaction_type}
        )
    return reaction, 'created' if created else 'updated'


def toggle_bookmark(user, post, remove=False):
    bookmark_object = Bookmark.objects.filter(
        post=post,
        user=user
    ).first()

    if remove and bookmark_object:
        bookmark_object.delete()
        return None

    bookmark = Bookmark.objects.get_or_create(
        post=post,
        user=user
    )
    return bookmark

def user_can_access_group(user, group):
    if group.visibility == StudyGroup.Visibility.PRIVATE:
        is_member = group.owner == user or GroupMembership.objects.filter(
            group=group,
            user=user,
            status=GroupMembership.Status.ACTIVE
        ).exists()

        if not is_member:
            return False
        return True
    return True


def user_can_manage_post(user, post):
    return post.group.membership.filter(user=user, status=GroupMembership.Status.ACTIVE, role=GroupMembership.Role.MODERATOR).exists() or post.group.owner == user
