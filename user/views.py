from django.contrib import messages
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from user.forms import UserLoginForm, UserRegisterForm, UserEditForm, ProfileEditForm
from user.models import Profile
from user.serializers import UserRegisterSerializer, UserProfileUpdateSerializer, UserLoginSerializer, \
    ChangePasswordSerializer, UserListSerializer


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

class UserProfileView(LoginRequiredMixin, DetailView):
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


class UserRegisterAPIView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)

        profile_serializer = UserProfileUpdateSerializer(
            user.profile,
            context=self.get_serializer_context(),
        )
        return Response(
            {
                'message': "User created successfully",
                'user': profile_serializer.data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )

class UserLoginAPIView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                'message': "You logged in successfully",
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )

class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile


class UserChangePasswordAPIView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        update_session_auth_hash(request, user)

        return Response(
            {'message': "Password changed successfully"},
            status=status.HTTP_200_OK,
        )


class UserListAPIView(generics.ListAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAdminUser]


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, ])
def logout_view(request):
    refresh_value = request.data.get('refresh')
    if not refresh_value:
        return Response(
            {'refresh': 'This field is required.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        token = RefreshToken(refresh_value)
        if str(token['user_id']) != str(request.user.pk):
            raise TokenError('Token does not belong to the current user.')
        token.blacklist()
    except (TokenError, KeyError):
        return Response(
            {'refresh': 'Token is invalid or expired.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {'message': "Logged out successfully"},
        status=status.HTTP_200_OK,
    )
