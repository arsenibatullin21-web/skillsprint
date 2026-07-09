from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import ListView

from study_groups.models import StudyGroup, GroupMembership


# Create your views here.

class MyGroupsView(LoginRequiredMixin, ListView):
    template_name = 'study_groups/my_groups.html'
    context_object_name = 'memberships'
    model = GroupMembership

    def get_queryset(self):
        queryset = GroupMembership.objects.filter(user=self.request.user)
        role = self.request.GET.get('role')
        if role and role != 'all':
            queryset = queryset.filter(role=role)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_groups = StudyGroup.objects.filter(membership__user=self.request.user)
        context['user_groups'] = user_groups
        context['owned_groups'] = user_groups.filter(owner=self.request.user)
        context['moderator_groups'] = user_groups.filter(membership__role=GroupMembership.Role.MODERATOR)
        context['public_groups'] = user_groups.filter(visibility=StudyGroup.Visibility.PUBLIC)
        context['joined_groups'] = user_groups.exclude(membership__role=GroupMembership.Role.OWNER)
        context['selected_role'] = self.request.GET.get('role')
        return context

    def get_template_names(self):
        if self.request.headers.get('HX-Request') == 'true':
            return ['study_groups/partial/my_groups_partial.html']
        return ['study_groups/my_groups.html']

