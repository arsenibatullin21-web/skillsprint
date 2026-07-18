from django.shortcuts import get_object_or_404
from rest_framework import permissions

from study_groups.models import GroupPost, StudyGroup, GroupMembership


class IsMember(permissions.BasePermission):
    def has_permission(self, request, view):
        group = get_object_or_404(StudyGroup, pk=view.kwargs.get('group_id'))
        is_member = group.owner == request.user or GroupMembership.objects.filter(
            group=group,
            user=request.user,
            status=GroupMembership.Status.ACTIVE
        ).exists()

        if not is_member:
            return False
        return True