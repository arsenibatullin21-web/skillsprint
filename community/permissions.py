from idlelib.rpc import request_queue

from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import permissions

from study_groups.models import GroupPost, StudyGroup, GroupMembership


class IsMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if 'group_id' in view.kwargs:
            group = get_object_or_404(StudyGroup, pk=view.kwargs.get('group_id'))
        elif 'post_id' in view.kwargs:
            post = get_object_or_404(GroupPost, pk=view.kwargs.get('post_id'))
            group = post.group

        is_member = group.owner == request.user or GroupMembership.objects.filter(
            group=group,
            user=request.user,
            status=GroupMembership.Status.ACTIVE
        ).exists()

        if not is_member:
            return False
        return True

class IsPostAuthorOwnerOrModerator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ['PUT', 'PATCH']:
            return obj.author == request.user

        if request.method == 'DELETE':
            return (
                obj.author == request.user
                or obj.group.owner == request.user
                or obj.group.membership.filter(
                    user=request.user,
                    status=GroupMembership.Status.ACTIVE,
                    role=GroupMembership.Role.MODERATOR,
                ).exists()
            )

        return False

class IsAuthor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user

class IsModeratorOrOwnerOrAuthor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        group = obj.post.group
        return (group.owner == request.user or GroupMembership.objects.filter(
            group=group,
            user=request.user,
            status=GroupMembership.Status.ACTIVE,
            role=GroupMembership.Role.MODERATOR
        ).exists() or obj.author == request.user)