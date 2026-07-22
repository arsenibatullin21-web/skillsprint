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
    path('posts/bookmarked/', views.BookmarkedPostsListView.as_view(), name='posts_bookmarked'),

    #drf urls
    path('api/v1/groups/<int:group_id>/posts/', views.PostListDetailAPIView.as_view(), name='api_posts_list'),
    path('api/v1/groups/<int:group_id>/posts/<int:pk>/', views.PostListDetailAPIView.as_view(), name='api_posts_detail'),
    path('api/v1/groups/<int:group_id>/posts/create/', views.PostCreateUpdateDeleteAPIView.as_view(), name='api_posts_create'),
    path('api/v1/groups/<int:group_id>/posts/<int:pk>/update/', views.PostCreateUpdateDeleteAPIView.as_view(), name='api_posts_update'),
    path('api/v1/groups/<int:group_id>/posts/<int:pk>/delete/', views.PostCreateUpdateDeleteAPIView.as_view(), name='api_posts_delete'),

    path('api/v1/posts/<int:post_id>/comments/', views.CommentListAPIView.as_view(), name='api_comments'),
    path('api/v1/posts/<int:post_id>/comments/create/', views.CommentCreateAPIView.as_view(), name='api_comments_create'),
    path('api/v1/posts/<int:post_id>/comments/<int:pk>/update/', views.CommentUpdateDeleteAPIView.as_view(), name='api_comments_update'),
    path('api/v1/posts/<int:post_id>/comments/<int:pk>/delete/', views.CommentUpdateDeleteAPIView.as_view(), name='api_comments_delete'),

    path('api/v1/posts/<int:post_id>/reactions/list/', views.ReactionListAPIView.as_view(), name='api_reactions'),
    path('api/v1/posts/<int:post_id>/reactions/', views.ReactionToggleAPIView.as_view(), name='api_reactions_toggle'),

    path('api/v1/bookmarks/list/', views.BookmarkListAPIView.as_view(), name='api_my_bookmarks'),
    path('api/v1/<int:post_id>/bookmarks/', views.BookmarkToggleAPIView.as_view(), name='api_bookmarks_toggle'),

]