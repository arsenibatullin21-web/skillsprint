from django.urls import path, include, re_path
from study_groups import views

app_name = 'study_groups'

urlpatterns = [
    path('', views.MyGroupsView.as_view(), name='my_groups'),
    path('create/', views.GroupCreateView.as_view(), name='create'),
    path('explore/', views.GroupExploreView.as_view(), name='explore')
]