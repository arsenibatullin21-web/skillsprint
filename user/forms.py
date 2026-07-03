from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UsernameField, UserCreationForm
from django.contrib.auth.password_validation import validate_password

from user.models import Profile


class UserLoginForm(AuthenticationForm):
    username = UsernameField(required=True)
    password = forms.CharField(required=True)

    class Meta:
        model = get_user_model()
        fields = ['username', 'password']

class UserRegisterForm(UserCreationForm):
    username = UsernameField(required=True)
    email = forms.EmailField(required=True)
    password1 = forms.CharField(required=True, validators=[validate_password, ])
    password2 = forms.CharField(required=True)

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def clean(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if password1 != password2:
            raise forms.ValidationError('Passwords do not match!')
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError('Email already exists!')
        if get_user_model().objects.filter(username=username).exists():
            raise forms.ValidationError('Username already exists!')


class UserEditForm(forms.ModelForm):

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name']

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['display_name', 'bio', 'avatar', 'location', 'website']


