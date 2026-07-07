from django.urls import path, include, re_path
from goals import views

app_name = 'goals'

urlpatterns = [
    path('', views.MyGoalsView.as_view(), name='my_goals'),
    path('create/', views.CreateGoalView.as_view(), name='create'),
    path('goals/<int:id>/', views.GoalDetailView.as_view(), name='detail'),
    path('goals/<int:id>/edit/', views.GoalUpdateView.as_view(), name='edit'),
    path('goals/<int:id>/delete/', views.GoalDeleteView.as_view(), name='delete'),
    path('goals/<int:id>/create/progress/', views.GoalProgressCreateView.as_view(), name='progress_update'),
    path('goals/explore/', views.GoalExploreView.as_view(), name='explore'),
    # path('goals/my/'),
    # path('goals/<int:id>')
]