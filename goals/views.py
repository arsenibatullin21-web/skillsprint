from datetime import timedelta

from django.db.models import Avg, Count, Q
from django.utils import timezone

from django.views.generic import ListView

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


