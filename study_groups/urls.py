from django.urls import path, include, re_path
from study_groups import views

app_name = 'study_groups'

urlpatterns = [
    path('', views.MyGroupsView.as_view(), name='my_groups'),
    path('create/', views.GroupCreateView.as_view(), name='create'),
    path('explore/', views.GroupExploreView.as_view(), name='explore'),
    path('detail/<int:id>/', views.GroupDetailView.as_view(), name='detail'),
    path('edit/<int:id>/', views.GroupUpdateView.as_view(), name='edit'),
    path('delete/<int:id>/', views.GroupDeleteView.as_view(), name='delete'),
    path('<int:id>/join/', views.GroupJoinView.as_view(), name='join'),
    path('<int:id>/leave/', views.GroupLeaveView.as_view(), name='leave'),
    path('<int:id>/requests/', views.GroupRequestView.as_view(), name='requests'),
    path('<int:id>/requests/accept/', views.UserAcceptView.as_view(), name='accept'),
    path('<int:id>/requests/reject/', views.UserRejectView.as_view(), name='reject'),
    path('<int:id>/members/', views.GroupMembersView.as_view(), name='members'),
    path('<int:group_id>/member/<int:membership_id>/promote/', views.MakeModeratorView.as_view(), name='promote'),
    path('<int:group_id>/member/<int:membership_id>/remove/', views.RemoveMemberView.as_view(), name='remove_member'),
    path('<int:group_id>/member/<int:membership_id>/promote/owner/', views.MakeOwnerView.as_view(), name='promote_owner'),
]
