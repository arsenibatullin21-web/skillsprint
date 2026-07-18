from django.urls import path
from community import views
app_name='community'

urlpatterns = [
    # django urls
    path('groups/<int:group_id>/', views.GroupFeedView.as_view(), name='feed'),
    path('groups/<int:group_id>/create/', views.PostCreateView.as_view(), name='post_create'),
    path('posts/<int:post_id>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    path('posts/<int:post_id>/update/', views.PostUpdateView.as_view(), name='post_update'),
    path('posts/<int:post_id>/detail/', views.PostDetailView.as_view(), name='post_detail'),
    path('posts/<int:post_id>/comments/create/', views.CommentCreateView.as_view(), name='comment_create'),
    path('posts/<int:post_id>/reaction/create/', views.ReactionCreateUpdateDeleteView.as_view(), name='reaction_create'),
    path('posts/<int:post_id>/bookmark/create/', views.BookmarkCreateDeleteView.as_view(), name='bookmark_create'),
    path('posts/<int:post_id>/comments/<int:comment_id>/update/', views.CommentUpdateView.as_view(), name='comment_update'),
    path('posts/<int:post_id>/comments/<int:comment_id>/delete/', views.CommentDeleteView.as_view(), name='comment_delete'),

]