from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, CreateView, DetailView, DeleteView, UpdateView
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy, reverse


from community.forms import PostCreateForm, CommentCreateForm
from community.models import Reaction, Comment, Bookmark
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
            ).exists()
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
        context['is_update'] = False
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
        ).exists()
        if not is_member:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.group = self.group
        form.instance.author = self.request.user
        return super().form_valid(form)



class PostDetailView(LoginRequiredMixin, DetailView):
    model = GroupPost
    template_name = 'community/post_detail.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        post = self.get_object()
        context = super().get_context_data(**kwargs)
        reaction = Reaction.objects.filter(post=post, user=self.request.user).first()
        context['user_reaction'] = reaction.type if reaction else None
        context['can_manage_post'] = post.group.membership.filter(user=self.request.user, status=GroupMembership.Status.ACTIVE, role=GroupMembership.Role.MODERATOR).exists() or post.group.owner == self.request.user
        context['helpful_count'] = post.reactions.filter(type=Reaction.Type.HELPFUL).count()
        context['celebrate_count'] = post.reactions.filter(type=Reaction.Type.CELEBRATE).count()
        context['like_count'] = post.reactions.filter(type=Reaction.Type.LIKE).count()
        context['is_bookmarked'] = post.bookmarks.filter(user=self.request.user).exists()
        context['comments_count'] = post.comments.count()
        context['reactions_count'] = post.reactions.count()
        context['bookmarks_count'] = post.bookmarks.count()
        context['comments'] = post.comments.filter(parent__isnull=True)
        context['comment_form'] = CommentCreateForm()
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    template_name = 'community/post_detail.html'
    form_class = CommentCreateForm


    def get_success_url(self):
        return reverse('community:post_detail', kwargs={'post_id': self.kwargs.get('post_id')})

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        post = get_object_or_404(GroupPost, pk=kwargs.get('post_id'))

        is_member = post.group.owner == user or GroupMembership.objects.filter(
            group=post.group,
            user=self.request.user,
            status=GroupMembership.Status.ACTIVE
        ).exists()

        if not is_member:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentCreateForm()
        return context

    def form_valid(self, form):
        post = get_object_or_404(GroupPost, pk=self.kwargs.get('post_id'))
        parent_id = self.request.POST.get('parent')
        form.instance.parent = None
        if parent_id:
            parent_comment = get_object_or_404(Comment, pk=parent_id)
            form.instance.parent = parent_comment
        form.instance.post = post
        form.instance.author = self.request.user
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Comment cannot be empty.")
        return redirect(self.get_success_url())


class ReactionCreateUpdateDeleteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        remove = self.request.POST.get('remove') == '1'
        reaction_type = self.request.POST.get('type')
        reaction = Reaction.objects.filter(
            post=self.post_object,
            user=self.request.user
        ).first()

        if reaction_type not in Reaction.Type.values:
            messages.error(request, 'Invalid reaction.')
            return redirect('community:post_detail', post_id=self.post_object.id)

        if remove and reaction and reaction.type == reaction_type:
            reaction.delete()
        else:
            reaction = Reaction.objects.update_or_create(
                post=self.post_object,
                user=self.request.user,
                defaults={'type': reaction_type}
            )

        return redirect('community:post_detail', post_id=self.post_object.id)

    def dispatch(self, request, *args, **kwargs):
        self.post_object = get_object_or_404(GroupPost, pk=kwargs.get('post_id'))
        user = self.request.user
        is_member = self.post_object.group.owner == user or GroupMembership.objects.filter(
            group=self.post_object.group,
            user=self.request.user,
            status=GroupMembership.Status.ACTIVE
        ).exists()

        if not is_member:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

class BookmarkCreateDeleteView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        remove = self.request.POST.get('remove') == '1'
        bookmark_object = Bookmark.objects.filter(
            post=self.post_object,
            user=self.request.user
        ).first()

        if remove and bookmark_object:
            bookmark_object.delete()
        else:
            Bookmark.objects.update_or_create(
                post=self.post_object,
                user=self.request.user
            )

        return redirect('community:post_detail', post_id=self.post_object.id)


    def dispatch(self, request, *args, **kwargs):
        self.post_object = get_object_or_404(GroupPost, pk=kwargs.get('post_id'))
        user = self.request.user
        is_member = self.post_object.group.owner == user or GroupMembership.objects.filter(
            group=self.post_object.group,
            user=self.request.user,
            status=GroupMembership.Status.ACTIVE
        ).exists()

        if not is_member:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = GroupPost
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        self.post_object = get_object_or_404(GroupPost, pk=kwargs.get('post_id'))

        is_moderator_owner = self.post_object.group.owner == request.user or GroupMembership.objects.filter(
            group=self.post_object.group,
            user=self.request.user,
            status=GroupMembership.Status.ACTIVE,
            role=GroupMembership.Role.MODERATOR,
        ).exists()

        if not is_moderator_owner:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)


    def get_success_url(self):
        return reverse('community:feed', kwargs={'group_id': self.post_object.group.id})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = GroupPost
    template_name = 'community/post_create.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'
    form_class = PostCreateForm

    def dispatch(self, request, *args, **kwargs):
        self.post_object = get_object_or_404(GroupPost, pk=kwargs.get('post_id'))
        user = self.request.user

        is_author = self.post_object.author == user

        if not is_author:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = self.post_object.group
        context['is_update'] = True
        return context

    def get_success_url(self):
        return reverse('community:post_detail', kwargs={'post_id': self.post_object.id})


