from django.contrib.auth.views import LogoutView
from django.urls import path
from user import views
from rest_framework_simplejwt.views import TokenRefreshView

app_name = 'user'

urlpatterns = [
    # Django URLs
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('profile/<int:user_id>/', views.UserProfileView.as_view(), name='profile'),
    path('logout/', LogoutView.as_view(next_page='user:login'), name='logout'),
    path('profile/edit/', views.user_edit, name='profile-edit'),

    # DRF URLs
    path('api/v1/register/', views.UserRegisterAPIView.as_view(), name='api-register'),
    path('api/v1/login/', views.UserLoginAPIView.as_view(), name='api-login'),
    path('api/v1/logout/', views.logout_view, name='api-logout'),
    path('api/v1/profile/', views.UserProfileAPIView.as_view(), name='api-profile'),
    path(
        'api/v1/changepassword/',
        views.UserChangePasswordAPIView.as_view(),
        name='api-change-password',
    ),
    path('api/v1/users/', views.UserListAPIView.as_view(), name='api-user-list'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
