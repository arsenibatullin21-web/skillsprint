from django.urls import path
from community import views
app_name='community'

urlpatterns = [
    path('groups/<int:group_id>/', views.GroupFeedView.as_view(), name='feed'),
    path('groups/<int:group_id>/create/', views.PostCreateView.as_view(), name='post_create'),
]