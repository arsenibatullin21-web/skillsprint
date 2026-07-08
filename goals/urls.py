from django.urls import path, include, re_path
from goals import views

app_name = 'goals'

urlpatterns = [
    # Django urls
    path('', views.MyGoalsView.as_view(), name='my_goals'),
    path('create/', views.CreateGoalView.as_view(), name='create'),
    path('goals/<int:id>/', views.GoalDetailView.as_view(), name='detail'),
    path('goals/<int:id>/edit/', views.GoalUpdateView.as_view(), name='edit'),
    path('goals/<int:id>/delete/', views.GoalDeleteView.as_view(), name='delete'),
    path('goals/<int:id>/create/progress/', views.GoalProgressCreateView.as_view(), name='progress_update'),
    path('goals/explore/', views.GoalExploreView.as_view(), name='explore'),
    path('goals/my/', views.MyAllGoalsView.as_view(), name='my_all_goals'),
    path('goals/public/<int:id>', views.PublicGoalView.as_view(), name='public_goal' ),


    # DRF urls
    path('api/v1/goals/', views.GoalsListAPIView.as_view(), name='api_my_all_goals'),
    path('api/v1/<int:pk>/goal/', views.GoalDetailApiView.as_view(), name='api_detail'),
    path('api/v1/goals/create/', views.GoalCreateAPIView.as_view(), name='api_create'),
    path('api/v1/goals/explore/', views.PublicGoalsListAPIView.as_view(), name='api_explore'),
    path('api/v1/<int:pk>/goal/edit/', views.GoalUpdateAPIView.as_view(), name='api_update'),
    path('api/v1/<int:pk>/progress/create/', views.ProgressCreateAPIView.as_view(), name='api_progress'),
    path('api/v1/delete/<int:pk>/goal/', views.GoalDeleteAPIView.as_view(), name='api_delete_goal'),

    path('api/v1/milestone/<int:pk>/create/', views.MilestoneCreateAPIView.as_view(), name='api_create_milestone'),
    path('api/v1/milestone/<int:pk>/update/', views.MilestoneUpdateAPIView.as_view(), name='api_update_milestone'),
    path('api/v1/milestone/<int:pk>/delete/', views.MilestoneDeleteAPIView.as_view(), name='api_delete_milestone')
    # path('api/v1/'),
]