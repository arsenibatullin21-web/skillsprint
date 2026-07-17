from tokenize import group

from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import permissions

from study_groups.models import GroupMembership, StudyGroup


class IsOwnerOrModeratorGroup(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ['PUT', 'PATCH']:
            if obj.membership.filter(Q(user=request.user) & Q(role=GroupMembership.Role.MODERATOR) & Q(status=GroupMembership.Status.ACTIVE)).exists() or obj.owner == request.user:
                return True
            return False

        if request.method in ['DELETE']:
            if obj.owner == request.user:
                return True
            return False

class IsOwnerOrModeratorMembership(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ['PUT', 'PATCH']:
            return (
                obj.group.owner == request.user
                or obj.group.membership.filter(
                    user=request.user,
                    role=GroupMembership.Role.MODERATOR,
                    status=GroupMembership.Status.ACTIVE,
                ).exists()
            )

        if request.method in ['DELETE']:
            return (
                obj.group.owner == request.user
                or obj.group.membership.filter(
                    user=request.user,
                    role=GroupMembership.Role.MODERATOR,
                    status=GroupMembership.Status.ACTIVE,
                ).exists()
            )

        return False

class IsAuthorOrOwnerOrModerator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ['PUT', 'PATCH']:
            return ( obj.author == request.user or
                    obj.group.owner == request.user
                    or obj.group.membership.filter(
                user=request.user,
                role=GroupMembership.Role.MODERATOR,
                status=GroupMembership.Status.ACTIVE,
            ).exists()
            )

        if request.method in ['DELETE']:
            return ( obj.author == request.user or
                    obj.group.owner == request.user
                    or obj.group.membership.filter(
                user=request.user,
                role=GroupMembership.Role.MODERATOR,
                status=GroupMembership.Status.ACTIVE,
            ).exists()
            )

        return False

class IsActiveMember(permissions.BasePermission):
    def has_permission(self, request, view):
        group = get_object_or_404(
            StudyGroup,
            pk=view.kwargs.get('group_id')
        )

        return (GroupMembership.objects.filter(
            Q(group__owner=request.user) |
            Q(
                user=request.user,
                status=GroupMembership.Status.ACTIVE,
                group=group
            )
        ).exists())

class IsModeratorOrOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, StudyGroup):
            group = obj
        else:
            group = obj.group

        return GroupMembership.objects.filter(
            Q(group__owner=request.user, group=group) |
            Q(
                user=request.user,
                group=group,
                status=GroupMembership.Status.ACTIVE,
                role=GroupMembership.Role.MODERATOR
              )
        ).exists()
