from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView

from user.forms import UserLoginForm, UserRegisterForm, UserEditForm, ProfileEditForm
from user.models import Profile

# Create your views here.

class UserLoginView(LoginView):
    form_class = UserLoginForm
    template_name = 'user/login.html'

    def get_success_url(self):
        return self.get_redirect_url() or reverse(
            'user:profile',
            kwargs={'user_id': self.request.user.pk},
        )

class UserRegisterView(CreateView):
    model = get_user_model()
    template_name = 'user/register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('user:login')

class UserProfileView(DetailView):
    model = get_user_model()
    template_name = 'user/profile.html'
    context_object_name = 'profile_user'
    pk_url_kwarg = 'user_id'


@login_required
@transaction.atomic
def user_edit(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    user_form = UserEditForm(
        request.POST or None,
        instance=request.user
    )
    profile_form = ProfileEditForm(
        request.POST or None,
        request.FILES or None,
        instance=profile
    )

    if request.method == 'POST':
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            messages.success(request, "Profile edited successfully!")
            return redirect('user:profile', user_id=request.user.id)

    return render(
        request,
        'user/profile_edit.html',
        {
            'user_form': user_form,
            'profile_form': profile_form,
        },
    )
