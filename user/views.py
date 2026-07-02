from django.contrib.auth.views import LoginView
from django.shortcuts import render

from user.forms import UserLoginForm


# Create your views here.

class UserLoginView(LoginView):
    form_class = UserLoginForm
    template_name = 'user/login.html'
    success_url = ''
