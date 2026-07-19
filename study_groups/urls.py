from django.urls import path, include, re_path
from study_groups import views

app_name = 'study_groups'

urlpatterns = [
    # django urls
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

    # drf urls
    path('api/v1/groups/', views.UserGroupListAPIView.as_view(), name='api_my_groups'),
    path('api/v1/explore/groups/', views.ExploreGroupListAPIView.as_view(), name='api_explore_groups'),
    path('api/v1/<int:pk>/group/', views.GroupDetailAPIView.as_view(), name='api_group_detail'),
    path('api/v1/create/', views.GroupCreateUpdateDestroyAPIView.as_view(), name='api_create'),
    path('api/v1/<int:pk>/update/', views.GroupCreateUpdateDestroyAPIView.as_view(), name='api_update'),
    path('api/v1/<int:pk>/destroy/', views.GroupCreateUpdateDestroyAPIView.as_view(), name='api_destroy'),

    path('api/v1/<int:group_id>/membership/', views.MembershipListDetailAPIView.as_view(), name='api_memberships'),
    path('api/v1/<int:group_id>/membership/<int:pk>/', views.MembershipListDetailAPIView.as_view(), name='api_membership_detail'),
    path('api/v1/membership/create/', views.MembershipCreateAPIView.as_view(), name='api_membership_create'),
    path('api/v1/<int:pk>/membership/update/', views.MembershipUpdateAPIView.as_view(), name='api_membership_update'),
    path('api/v1/<int:pk>/membership/destroy/', views.MembershipUpdateAPIView.as_view(), name='api_membership_destroy'),


    path('api/v1/resources/<int:group_id>/', views.ResourceListDetailAPIView.as_view(), name='api_resource_list'),
    path('api/v1/resources/<int:group_id>/<int:pk>/', views.ResourceListDetailAPIView.as_view(), name='api_resource_detail'),
    path('api/v1/resources/<int:group_id>/create/', views.ResourceCreateUpdateAPIView.as_view(), name='api_resource_create'),
    path('api/v1/resources/<int:group_id>/update/<int:pk>/', views.ResourceCreateUpdateAPIView.as_view(), name='api_resource_update'),
    path('api/v1/resources/<int:group_id>/destroy/<int:pk>/', views.ResourceCreateUpdateAPIView.as_view(), name='api_resource_destroy'),

]
