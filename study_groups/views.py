from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count
from django.db.models.functions import Lower, Trim
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib import messages
from goals.views import CreateGoalView
from study_groups.forms import GroupCreateForm
from study_groups.models import StudyGroup, GroupMembership


# Create your views here.

class MyGroupsView(LoginRequiredMixin, ListView):
    template_name = 'study_groups/my_groups.html'
    context_object_name = 'memberships'
    model = GroupMembership

    def get_queryset(self):
        queryset = GroupMembership.objects.filter(user=self.request.user, status=GroupMembership.Status.ACTIVE)
        role = self.request.GET.get('role')
        if role and role != 'all':
            queryset = queryset.filter(role=role)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_groups = StudyGroup.objects.filter(membership__user=self.request.user, membership__status=GroupMembership.Status.ACTIVE)
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

class GroupCreateView(LoginRequiredMixin,CreateView):
    model = StudyGroup
    template_name = 'study_groups/group_create.html'
    success_url = reverse_lazy('study_groups:my_groups')
    form_class = GroupCreateForm

    # def get_success_url(self):
    #     return reverse('')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)

        GroupMembership.objects.create(
            group=self.object,
            user=self.request.user,
            role=GroupMembership.Role.OWNER,
            status=GroupMembership.Status.ACTIVE
        )
        return response

class GroupExploreView(ListView):
    model = StudyGroup
    template_name = 'study_groups/group_explore.html'
    context_object_name = 'groups'

    def get_queryset(self):
        queryset = StudyGroup.objects.filter(
            visibility=StudyGroup.Visibility.PUBLIC
        ).annotate(
            members_count=Count(
                'membership',
                filter=Q(membership__status=GroupMembership.Status.ACTIVE),
            ),
            clean_topic=Lower(Trim('topic')),
        )

        search = self.request.GET.get('search')
        topic = self.request.GET.get('topic')
        size = self.request.GET.get('size')
        sort = self.request.GET.get('sort')

        if search:
            queryset = queryset.filter(Q(name__icontains=search) & Q(topic__icontains=search) & Q(description__icontains=search))

        if topic and topic != 'all':
            queryset = queryset.filter(clean_topic=topic)

        if size and size != 'all':
            if size == 'small':
                queryset = queryset.filter(members_count__gte=1, members_count__lte=10)
            elif size == 'medium':
                queryset = queryset.filter(members_count__gte=11, members_count__lte=30)
            elif size == 'large':
                queryset = queryset.filter(members_count__gte=31)

        if sort and sort != 'recommended':
            if sort == 'newest':
                queryset = queryset.order_by('-created_at')
            elif sort == 'members':
                queryset = queryset.order_by('-members_count')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        topics = StudyGroup.objects.annotate(
            clean_topic=Lower(Trim('topic'))
        ).exclude(
            clean_topic=''
        ).values_list(
            'clean_topic',
            flat=True
        ).distinct().order_by('clean_topic')
        context['topics'] = topics
        context['selected_topic'] = self.request.GET.get('topic')
        context['selected_size'] = self.request.GET.get('size')
        context['selected_sort'] = self.request.GET.get('sort')
        context['selected_search'] = self.request.GET.get('search')
        return context

    def get_template_names(self):
        if self.request.headers.get('HX-Request') == 'true':
            return ['study_groups/partial/group_explore_partial.html']
        return ['study_groups/group_explore.html']



class GroupDetailView(DetailView):
    model = StudyGroup
    context_object_name = 'group'
    pk_url_kwarg = 'id'
    template_name = 'study_groups/group_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        membership = None
        if self.request.user.is_authenticated:
            membership = GroupMembership.objects.filter(
                group=self.object,
                user=self.request.user
            ).first()
        context['membership'] = membership
        return context


class GroupUpdateView(LoginRequiredMixin, UpdateView):
    model = StudyGroup
    template_name = 'study_groups/group_update.html'
    context_object_name = 'group'
    pk_url_kwarg = 'id'
    form_class = GroupCreateForm
    success_url = reverse_lazy('study_groups:my_groups')

    def get_queryset(self):
        return StudyGroup.objects.filter(
            Q(owner=self.request.user) |
            Q(
                membership__user=self.request.user,
                membership__role=GroupMembership.Role.MODERATOR,
                membership__status=GroupMembership.Status.ACTIVE,
            )
        ).distinct()

class GroupDeleteView(DeleteView):
    model = StudyGroup
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('study_groups:my_groups')

    def get_queryset(self):
        return StudyGroup.objects.filter(
            Q(owner=self.request.user)
        )

class GroupJoinView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        group = get_object_or_404(StudyGroup, pk=kwargs['id'])

        if group.owner == self.request.user:
            messages.info(request,'You are owner of this group')
            return redirect('study_groups:detail', id = group.id)


        membership, created = GroupMembership.objects.get_or_create(
            group=group,
            user=request.user,
            defaults={
                'role': GroupMembership.Role.MEMBER,
                'status': (
                    GroupMembership.Status.ACTIVE
                    if group.visibility == StudyGroup.Visibility.PUBLIC
                    else GroupMembership.Status.PENDING
                )
            }
        )

        if not created:
            if membership.status == GroupMembership.Status.ACTIVE:
                messages.info(request, 'You are already in the group')
            elif membership.status == GroupMembership.Status.PENDING:
                messages.info(request,'Your request is not accepted yet')
            elif membership.status == GroupMembership.Status.REJECTED:
                membership.status = GroupMembership.Status.PENDING
                membership.save(update_fields=['status'])
                messages.success(request, 'Your join request was sent again')

            return redirect('study_groups:detail', id=group.id)

        if membership.status == GroupMembership.Status.ACTIVE:
            messages.success(request, 'You joined the group successfully')
        elif membership.status == GroupMembership.Status.PENDING:
            messages.info(request, 'Request to join was sent')

        return redirect('study_groups:detail', id=group.id)


class GroupLeaveView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        group = get_object_or_404(StudyGroup, pk=kwargs['id'])

        if group.owner == request.user:
            messages.info(request, 'You have to pass your ownership to leave the group')
            return redirect('study_groups:detail', id=group.id)

        membership = GroupMembership.objects.filter(
            group=group,
            user=request.user
        ).first()

        if membership:
            membership.delete()
            messages.success(request, "You left the group")
            return redirect('study_groups:detail', id=group.id)
        else:
            messages.info(request, 'You are not member of the group')
            return redirect('study_groups:detail', id=group.id)


