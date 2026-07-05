from django.urls import path, include, re_path
from goals import views

app_name = 'goals'

urlpatterns = [
    path('', views.MyGoalsView.as_view(), name='my_goals'),
    path('create/', views.CreateGoalView.as_view(), name='create'),
    path('goals/<int:id>/', views.GoalDetailView.as_view(), name='detail'),
]