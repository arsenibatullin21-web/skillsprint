from django.contrib.auth import get_user, get_user_model
from django.contrib.auth.views import LoginView
from django.shortcuts import render
from django.views.generic import CreateView
from rest_framework.reverse import reverse_lazy

from user.forms import UserLoginForm, UserRegisterForm


# Create your views here.

class UserLoginView(LoginView):
    form_class = UserLoginForm
    template_name = 'user/login.html'
    success_url = ''

class UserRegisterView(CreateView):
    model = get_user_model()
    template_name = 'user/register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('user:login')

