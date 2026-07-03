from django.contrib.auth.views import LogoutView
from django.urls import path
from user import views
app_name = 'user'

urlpatterns = [
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('profile/<int:user_id>/', views.UserProfileView.as_view(), name='profile'),
    path('logout/', LogoutView.as_view(next_page='main:home'), name='logout'),
    # path('changepassword/')
]