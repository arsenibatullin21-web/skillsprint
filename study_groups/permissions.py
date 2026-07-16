from django.db.models import Q
from rest_framework import permissions

from study_groups.models import GroupMembership


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