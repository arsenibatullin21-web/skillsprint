from tokenize import group

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, CreateView
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy, reverse

from community.forms import PostCreateForm
from study_groups.models import GroupPost, StudyGroup, GroupMembership


# Create your views here.
class GroupFeedView(LoginRequiredMixin, ListView):
    model = GroupPost
    template_name = 'community/feed.html'
    context_object_name = 'posts'

    def dispatch(self, request, *args, **kwargs):
        self.group = get_object_or_404(StudyGroup, pk=kwargs.get('group_id'))
        if self.group.visibility == StudyGroup.Visibility.PRIVATE:
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


class PostCreateView(LoginRequiredMixin, CreateView):
    model = GroupPost
    template_name = 'community/post_create.html'
    form_class = PostCreateForm
    pk_url_kwarg = 'group_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = self.group
        return context

    def get_success_url(self):
        return reverse(
            'community:feed',
            kwargs={'group_id': self.kwargs.get('group_id')}
        )

    def dispatch(self, request, *args, **kwargs):
        self.group = get_object_or_404(StudyGroup, pk=kwargs.get('group_id'))
        is_member = self.group.owner == self.request.user or GroupMembership.objects.filter(
            group=self.group,
            user=self.request.user,
            status=GroupMembership.Status.ACTIVE
        )
        if not is_member:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.group = self.group
        form.instance.author = self.request.user
        return super().form_valid(form)
