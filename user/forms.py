from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UsernameField


class UserLoginForm(AuthenticationForm):
    username = UsernameField(required=True)
    password = forms.CharField(required=True)

    class Meta:
        model = get_user_model()
        fields = ['username', 'password']



