from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from rest_framework.exceptions import PermissionDenied

from study_groups.models import GroupPost, StudyGroup, GroupMembership


# Create your views here.
class GroupFeedView(LoginRequiredMixin, ListView):
    model = GroupPost
    template_name = 'community/feed.html'
    context_object_name = 'posts'

    def dispatch(self, request, *args, **kwargs):
        is_member = self.request.user == self.group.owner or GroupMembership.objects.filter(
            group=self.group,
            user=self.request.user,
            status=GroupMembership.Status.ACTIVE
        )
        if not is_member:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        self.group = get_object_or_404(StudyGroup, pk=self.kwargs.get('group_id'))
        queryset = GroupPost.objects.select_related('group', 'author').filter(group=self.group)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = self.group
        return context
