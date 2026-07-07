from datetime import timedelta
from gc import get_objects

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Avg, Count, Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.context_processors import request
from django.utils import timezone

from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse

from goals.forms import GoalCreateForm, MilestoneFormSet, MilestoneUpdateForm, ProgressCreateForm
from goals.models import LearningGoals, ProgressEntry


class MyGoalsView(ListView):
    template_name = 'goals/home.html'
    context_object_name = 'goals'
    model = LearningGoals

    def get_context_data(self, **kwargs):
        week_labels = ["M", "T", "W", "T", "F", "S", "S"]
        week_days = []

        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        week_end = today + timedelta(days=7)
        goals = self.object_list

        week_start = today - timedelta(days=today.weekday())
        week_end2 = week_start + timedelta(days=6)
        activity_dates = set(
            ProgressEntry.objects.filter(
                goal__owner=self.request.user,
                created_at__date__range=(week_start, week_end2)
            ).dates(
                "created_at",
                "day",
            )
        )

        for index, label in enumerate(week_labels):
            day = week_start + timedelta(days=index)

            week_days.append({
                "label": label,
                "date": day,
                "completed": day in activity_dates,
                "is_today": day==today
            })

        active_goals = goals.filter(status=LearningGoals.Status.ACTIVE)
        average_progress = active_goals.aggregate(
            average=Avg("progress_percent")
        )["average"]



        context['active_goals'] = active_goals
        context['completed_goals'] = goals.filter(
            status=LearningGoals.Status.COMPLETED
        )
        context['upcoming_goals'] = goals.filter(
            status=LearningGoals.Status.ACTIVE,
            deadline__gte=today,
            deadline__lte=week_end,
        ).order_by("deadline")
        # context['study_groups'] = self.request.user.study_groups
        context['recent_activity'] = ProgressEntry.objects.filter(goal__owner=self.request.user).select_related("goal").order_by("-created_at")[:5]
        context['avg_progress'] = round(average_progress or 0)
        context['learning_days'] = len(activity_dates)
        context['week_days'] = week_days
        return context

    def get_queryset(self):
        return (
            LearningGoals.objects
            .filter(owner=self.request.user)
            .annotate(
                milestones_total=Count("milestones", distinct=True),
                milestones_completed=Count(
                    "milestones",
                    filter=Q(milestones__is_completed=True),
                    distinct=True,
                ),
            )
        )

class CreateGoalView(LoginRequiredMixin,CreateView):
    model = LearningGoals
    template_name = 'goals/goal_create.html'
    success_url = reverse_lazy('goals:my_goals')
    form_class = GoalCreateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['milestone_formset'] = MilestoneFormSet(
            self.request.POST or None,
            prefix="milestones",
            instance=self.object,
        )
        return context


    def form_valid(self, form):
        milestone_formset = MilestoneFormSet(
            data=self.request.POST,
            instance=self.object,
            prefix="milestones",
        )

        if not milestone_formset.is_valid():
            return self.form_invalid(form)

        with transaction.atomic():
            self.object = form.save(commit=False)
            self.object.owner = self.request.user
            self.object.save()

            milestone_formset.instance = self.object
            milestones = milestone_formset.save(commit=False)

            for position, milestone in enumerate(milestones, start=1):
                milestone.goal = self.object
                milestone.position = position
                milestone.save()

        return HttpResponseRedirect(self.get_success_url())


class GoalDetailView(DetailView):
    model = LearningGoals
    template_name = 'goals/goal_detail.html'
    context_object_name = 'goal'
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['milestone_next'] = self.object.milestones.filter(
            is_completed=False,
        ).order_by('position').first()
        return context

class GoalUpdateView(LoginRequiredMixin, UpdateView):
    model = LearningGoals
    template_name = 'goals/goal_update.html'
    context_object_name = 'goal'
    pk_url_kwarg = 'id'
    form_class = GoalCreateForm



    def form_valid(self, form):
        context = self.get_context_data(form=form)
        formset = context['milestone_formset']

        if not formset.is_valid():
            return self.form_invalid(form)


        with transaction.atomic():
            self.object = form.save()

            formset.instance = self.object
            formset.save()

            position = 1

            for milestone_form in formset.forms:
                cleaned_data = milestone_form.cleaned_data
                if not cleaned_data:
                    continue
                if cleaned_data.get("DELETE"):
                    continue

                milestone = milestone_form.instance

                if milestone.pk:
                    milestone.position = position
                    milestone.save(update_fields=['position'])
                    position += 1

            return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('goals:detail', kwargs={'id': self.object.pk})



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['milestone_formset'] = MilestoneUpdateForm(
            self.request.POST or None,
            prefix='milestone',
            instance=self.object
        )
        return context

    def get_queryset(self):
        return LearningGoals.objects.filter(
            owner=self.request.user
        )


class GoalDeleteView(LoginRequiredMixin, DeleteView):
    model = LearningGoals
    success_url = reverse_lazy('goals:my_goals')
    pk_url_kwarg = 'id'

    def get_queryset(self):
        return LearningGoals.objects.filter(owner=self.request.user)

class GoalProgressCreateView(LoginRequiredMixin, CreateView):
    template_name = 'goals/progress_update.html'
    context_object_name = 'progress'
    model = ProgressEntry
    pk_url_kwarg = 'id'
    form_class = ProgressCreateForm


    def get_context_data(self, **kwargs):
        goal = get_object_or_404(
            LearningGoals.objects.annotate(total_milestones=Count('milestones', distinct=True), completed_milestones=Count('milestones', filter=Q(milestones__is_completed=True), distinct=True)),
            pk=self.kwargs['id'],
            owner=self.request.user
        )
        self.goal = goal
        context = super().get_context_data(**kwargs)
        context['previous_progress'] = ProgressEntry.objects.filter(goal=goal).order_by('-created_at').first()
        context['goal'] = goal
        return context

    def get_success_url(self):
        return reverse('goals:detail', kwargs={"id": self.goal.id})

    @transaction.atomic()
    def form_valid(self, form):
        goal = get_object_or_404(LearningGoals, pk=self.kwargs['id'], owner=self.request.user)

        form.instance.goal = goal
        progress_percent = form.cleaned_data['progress_percent']
        goal.progress_percent = progress_percent
        if progress_percent == 100:
            goal.status = LearningGoals.Status.COMPLETED
        goal.save(update_fields=['progress_percent'])
        self.goal = goal
        return super().form_valid(form)


class GoalExploreView(ListView):
    template_name = 'goals/explore_goals.html'
    context_object_name = 'goals'
    model = LearningGoals

    def get_queryset(self):
        queryset = LearningGoals.objects.filter(visibility=LearningGoals.Visibility.PUBLIC).annotate(
            total_milestones=Count('milestones', distinct=True), completed_milestones=Count('milestones', filter=Q(milestones__is_completed=True), distinct=True)
        )

        search = self.request.GET.get('goal-search', None)
        status = self.request.GET.get('status', None)
        progress = self.request.GET.get('progress', None)
        sort = self.request.GET.get('sort', None)

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(owner__first_name__icontains=search) |
                Q(owner__last_name__icontains=search) |
                Q(description__icontains=search)
            )

        if status and status != 'all':
            queryset = queryset.filter(status=status)

        if progress and progress != 'all':
            if progress == 'starting':
                queryset = queryset.filter(Q(progress_percent__gte=0) & Q(progress_percent__lte=25))
            elif progress == 'underway':
                queryset = queryset.filter(Q(progress_percent__gte=26) & Q(progress_percent__lte=74))
            elif progress == 'near':
                queryset = queryset.filter(Q(progress_percent__gte=75) & Q(progress_percent__lte=99))
            elif progress == 'complete':
                queryset = queryset.filter(progress_percent=100)

        if sort:
            if sort == 'newest':
                queryset = queryset.order_by('-created_at')
            elif sort == 'deadline':
                queryset = queryset.order_by('deadline')
            elif sort == 'progress':
                queryset = queryset.order_by('-progress_percent')


        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('goal-search', None)
        context['selected_status'] = self.request.GET.get('status', None)
        context['selected_progress'] = self.request.GET.get('progress', None)
        context['selected_sort'] = self.request.GET.get('sort', None)
        return context

    def get_template_names(self):
        if self.request.headers.get('HX-Request') == 'true':
            return ['goals/explore_goal_partial.html']
        return ['goals/explore_goals.html']

class MyAllGoalsView(ListView):
    template_name = 'goals/all_goals.html'
    model = LearningGoals
    context_object_name = 'goals'

    def get_queryset(self):
        queryset = LearningGoals.objects.filter(owner=self.request.user).annotate(
            total_milestones=Count('milestones', distinct=True),
            completed_milestones=Count('milestones', filter=Q(milestones__is_completed=True))
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
