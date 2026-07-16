from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count, Case, When, Value, BooleanField
from django.db.models.functions import Lower, Trim
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.text import slugify
from django.views import View
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib import messages
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from goals.views import CreateGoalView
from study_groups.forms import GroupCreateForm
from study_groups.models import StudyGroup, GroupMembership, GroupPost
from rest_framework import generics, permissions, mixins, status

from study_groups.permissions import IsOwnerOrModeratorGroup, IsOwnerOrModeratorMembership, IsAuthorOrOwnerOrModerator
from study_groups.serializers import GroupDetailSerializer, UserGroupsSerializer, ExploreGroupsSerializer, \
    GroupCreateUpdateSerializer, MembershipSerializer, MembershipCreateSerializer, MembershipUpdateSerializer, \
    PostListDetailSerializer, PostCreateUpdateSerializer


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


class GroupRequestView(LoginRequiredMixin, ListView):
    model = GroupMembership
    template_name = 'study_groups/group_requests.html'
    context_object_name = 'memberships'

    def dispatch(self, request, *args, **kwargs):
        self.group =  get_object_or_404(StudyGroup, pk=kwargs.get('id'))
        user = request.user
        membership = GroupMembership.objects.filter(group=self.group, user=user).first()

        if not membership:
            messages.error(request, 'You are not a member of the group')
            return redirect('study_groups:detail', id=self.group.id)

        if not (membership.status == GroupMembership.Status.ACTIVE and (self.group.owner == request.user or membership.role == GroupMembership.Role.MODERATOR)):
            messages.error(request, "You don't have access to this action")
            return redirect('study_groups:detail', id=self.group.id)

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return GroupMembership.objects.filter(group=self.group, role=GroupMembership.Role.MEMBER)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pending'] = GroupMembership.objects.filter(group=self.group, status=GroupMembership.Status.PENDING)
        context['accepted'] = GroupMembership.objects.filter(Q(group=self.group) & Q(status=GroupMembership.Status.ACTIVE) & Q(role=GroupMembership.Role.MEMBER))
        context['rejected'] = GroupMembership.objects.filter(group=self.group, status=GroupMembership.Status.REJECTED)
        context['group'] = self.group
        return context

class UserAcceptView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        group = get_object_or_404(StudyGroup, pk=kwargs.get('id'))
        membership = get_object_or_404(
            GroupMembership,
            pk=request.POST.get('membership_id'),
            group=group,
            status=GroupMembership.Status.PENDING,
        )
        membership.status = GroupMembership.Status.ACTIVE
        membership.save(update_fields=['status'])
        messages.success(request, f'{membership.user.username} accepted successfully')
        return redirect('study_groups:requests', id=group.id)

class UserRejectView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        group = get_object_or_404(StudyGroup, pk=kwargs.get('id'))
        membership = get_object_or_404(
            GroupMembership,
            pk=request.POST.get('membership_id'),
            group=group,
            status=GroupMembership.Status.PENDING,
        )
        membership.status = GroupMembership.Status.REJECTED
        membership.save(update_fields=['status'])
        messages.success(request, f'{membership.user.username} rejected successfully')
        return redirect('study_groups:requests', id=group.id)

class GroupMembersView(ListView):
    model = GroupMembership
    context_object_name = 'memberships'
    template_name = 'study_groups/group_members.html'

    def get_queryset(self):
        self.group = StudyGroup.objects.filter(id=self.kwargs.get('id')).first()
        queryset = GroupMembership.objects.filter(group=self.group, status=GroupMembership.Status.ACTIVE).annotate(
            posts_count=Count('user__posts', filter=Q(user__posts__group=self.group), distinct=True),
            is_moderator=Case(
                When(role=GroupMembership.Role.MODERATOR, then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            )
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['moderators'] = self.get_queryset().filter(role=GroupMembership.Role.MODERATOR)
        context['rejected'] = self.get_queryset().filter(status=GroupMembership.Status.REJECTED)
        context['pending'] = self.get_queryset().filter(status=GroupMembership.Status.PENDING)
        context['group'] = self.group
        context['last_joined'] = self.get_queryset().order_by('joined_at').first()
        context['current_member'] = GroupMembership.objects.filter(group=self.group, user=self.request.user).first()
        return context

class MakeModeratorView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        group = get_object_or_404(StudyGroup, pk=kwargs.get('group_id'))
        membership = get_object_or_404(GroupMembership, group=group, pk=kwargs.get('membership_id'))


        if not membership.role == GroupMembership.Role.MEMBER:
            messages.error(request, 'Member is already a moderator')
            return redirect('study_groups:members', id=group.id)


        membership.role = GroupMembership.Role.MODERATOR
        membership.save(update_fields=['role'])
        messages.success(request, f'{membership.user.username} became a moderator')
        return redirect('study_groups:members', id=group.id)


class RemoveMemberView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        group = get_object_or_404(StudyGroup, pk=kwargs.get('group_id'))
        membership = get_object_or_404(GroupMembership, group=group, pk=kwargs.get('membership_id'))


        if membership.role == GroupMembership.Role.OWNER or membership.user == group.owner:
            messages.error(request, 'Owner cannot be removed from the group')
            return redirect('study_groups:members', id=group.id)

        username = membership.user.username
        membership.delete()
        messages.success(request, f'{username} was removed from the group')
        return redirect('study_groups:members', id=group.id)

class MakeOwnerView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        group = get_object_or_404(StudyGroup, pk=kwargs.get('group_id'))
        membership = get_object_or_404(GroupMembership, group=group, pk=kwargs.get('membership_id'))
        membership_owner = GroupMembership.objects.filter(group=group, role=GroupMembership.Role.OWNER).first()

        if membership.role != GroupMembership.Role.MODERATOR:
            messages.error(request, 'Member is not a moderator')
            return redirect('study_groups:members', id=group.id)


        membership.role = GroupMembership.Role.OWNER
        membership.save(update_fields=['role'])

        membership_owner.role = GroupMembership.Role.MODERATOR
        membership_owner.save(update_fields=['role'])
        messages.success(request, f'{membership.user.username} became the owner')
        return redirect('study_groups:members', id=group.id)


class UserGroupListAPIView(generics.ListAPIView):
    '''User's own groups'''
    serializer_class = UserGroupsSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get_queryset(self):
        return StudyGroup.objects.filter(membership__user=self.request.user, membership__status=GroupMembership.Status.ACTIVE)


class ExploreGroupListAPIView(generics.ListAPIView):
    '''Explore groups'''
    serializer_class = ExploreGroupsSerializer
    permission_classes = [permissions.IsAuthenticated, ]
    queryset = StudyGroup.objects.all()

class GroupDetailAPIView(generics.RetrieveAPIView):
    serializer_class = GroupDetailSerializer
    permission_classes = [permissions.IsAuthenticated, ]
    queryset = StudyGroup.objects.all()

class GroupCreateUpdateDestroyAPIView(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin ,generics.GenericAPIView):
    serializer_class = GroupCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrModeratorGroup]

    def get_queryset(self):
        return StudyGroup.objects.filter(Q(owner=self.request.user) | (Q(membership__user=self.request.user) & Q(membership__role=GroupMembership.Role.MODERATOR))).distinct()

    def post(self, request, *args, **kwargs):
        return self.create(request*args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class MembershipListDetailAPIView(mixins.ListModelMixin, mixins.RetrieveModelMixin, generics.GenericAPIView):
    serializer_class = MembershipSerializer
    permission_classes = [permissions.IsAuthenticated, ]


    def get_queryset(self):
        group = get_object_or_404(StudyGroup, pk=self.kwargs.get('group_id'))
        queryset = GroupMembership.objects.filter(group=group)
        return queryset

    def get(self, request, *args, **kwargs):
        if 'pk' in kwargs:
            return self.retrieve(request,*args, **kwargs)
        return self.list(request,*args, **kwargs)

class MembershipCreateAPIView(generics.CreateAPIView):
    serializer_class = MembershipCreateSerializer
    permission_classes = [permissions.IsAuthenticated ]


class MembershipUpdateAPIView(mixins.UpdateModelMixin, mixins.DestroyModelMixin,generics.GenericAPIView):
    serializer_class = MembershipUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrModeratorMembership]

    def get_queryset(self):
        user = self.request.user
        return GroupMembership.objects.filter(Q(group__owner=user) | Q(
            group__membership__user=user, group__membership__role=GroupMembership.Role.MODERATOR, group__membership__status=GroupMembership.Status.ACTIVE
        ))

    def post(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class PostListDetailAPIView(mixins.ListModelMixin, mixins.RetrieveModelMixin, generics.GenericAPIView):
    '''To se all posts of one group/To see one post's detail of ont group'''
    serializer_class = PostListDetailSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get_queryset(self):
        group_id = self.kwargs.get('group_id')
        group = get_object_or_404(StudyGroup, pk=group_id)
        return GroupPost.objects.filter(group=group)

    def get(self, request, *args, **kwargs):
        if 'pk' in self.kwargs:
            return self.retrieve(request, *args, **kwargs)
        return self.list(request, *args, **kwargs)

class PostCreateUpdateAPIView(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    serializer_class = PostCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrOwnerOrModerator]


    def get_queryset(self):
        group = get_object_or_404(StudyGroup, pk=self.kwargs.get('group_id'))
        return GroupPost.objects.filter(Q(group=group) & (Q(group__owner=self.request.user) | Q(group__membership__user=self.request.user, group__membership__status=GroupMembership.Status.ACTIVE, group__membership__role=GroupMembership.Role.MODERATOR) | Q(author=self.request.user))).distinct()

    def perform_create(self, serializer):
        group_id = self.kwargs.get('group_id')
        group = get_object_or_404(StudyGroup, pk=group_id)

        is_member = GroupMembership.objects.filter(
            group=group,
            user=self.request.user,
            status=GroupMembership.Status.ACTIVE
        ).exists()

        if not is_member:
            raise PermissionDenied(
                'You must be an active member to create posts.'
            )
        serializer.save(group=group, author=self.request.user)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)






