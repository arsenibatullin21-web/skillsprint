from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken

from user.models import User


class ProfileEditTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='learner',
            email='learner@example.com',
            password='Strong-password-123',
        )
        self.edit_url = reverse('user:profile-edit')

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(self.edit_url)

        self.assertRedirects(
            response,
            f"{reverse('user:login')}?next={self.edit_url}",
        )

    def test_authenticated_user_can_open_edit_page(self):
        self.client.force_login(self.user)

        response = self.client.get(self.edit_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/profile_edit.html')

    def test_authenticated_user_can_update_profile(self):
        self.client.force_login(self.user)

        response = self.client.post(
            self.edit_url,
            {
                'first_name': 'Alex',
                'last_name': 'Smith',
                'display_name': 'Alex S.',
                'bio': 'Learning Django.',
                'location': 'Qyzylorda',
                'website': 'https://example.com',
            },
        )

        self.user.refresh_from_db()
        self.user.profile.refresh_from_db()

        self.assertRedirects(
            response,
            reverse('user:profile', kwargs={'user_id': self.user.pk}),
        )
        self.assertEqual(self.user.first_name, 'Alex')
        self.assertEqual(self.user.last_name, 'Smith')
        self.assertEqual(self.user.profile.display_name, 'Alex S.')
        self.assertEqual(self.user.profile.bio, 'Learning Django.')


class LoginRedirectTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='login-user',
            email='login@example.com',
            password='Strong-password-123',
        )

    def test_login_redirects_to_user_profile_by_default(self):
        response = self.client.post(
            reverse('user:login'),
            {
                'username': self.user.username,
                'password': 'Strong-password-123',
            },
        )

        self.assertRedirects(
            response,
            reverse('user:profile', kwargs={'user_id': self.user.pk}),
        )

    def test_login_respects_safe_next_url(self):
        edit_url = reverse('user:profile-edit')

        response = self.client.post(
            reverse('user:login'),
            {
                'username': self.user.username,
                'password': 'Strong-password-123',
                'next': edit_url,
            },
        )

        self.assertRedirects(response, edit_url)


class UserAPITests(APITestCase):
    def setUp(self):
        self.password = 'Strong-password-123'
        self.user = User.objects.create_user(
            username='api-user',
            email='api-user@example.com',
            password=self.password,
        )

    def authenticate(self):
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}',
        )
        return refresh

    def test_registration_creates_user_profile_and_tokens(self):
        response = self.client.post(
            reverse('user:api-register'),
            {
                'username': 'new-api-user',
                'email': 'NEW-API-USER@example.com',
                'first_name': 'New',
                'last_name': 'User',
                'password': 'Another-strong-password-123',
                'password_confirm': 'Another-strong-password-123',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_user = User.objects.get(username='new-api-user')
        self.assertTrue(created_user.check_password(
            'Another-strong-password-123'
        ))
        self.assertEqual(created_user.email, 'new-api-user@example.com')
        self.assertTrue(hasattr(created_user, 'profile'))
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_returns_jwt_tokens(self):
        response = self.client.post(
            reverse('user:api-login'),
            {
                'username': self.user.username,
                'password': self.password,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_jwt_user_can_read_and_update_own_profile(self):
        self.authenticate()

        get_response = self.client.get(reverse('user:api-profile'))
        patch_response = self.client.patch(
            reverse('user:api-profile'),
            {
                'first_name': 'Updated',
                'display_name': 'Updated API User',
                'bio': 'Learning DRF.',
            },
            format='json',
        )

        self.user.refresh_from_db()
        self.user.profile.refresh_from_db()

        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(
            self.user.profile.display_name,
            'Updated API User',
        )

    def test_user_can_change_password(self):
        self.authenticate()

        response = self.client.post(
            reverse('user:api-change-password'),
            {
                'old_password': self.password,
                'new_password': 'Changed-password-456',
                'new_password_confirm': 'Changed-password-456',
            },
            format='json',
        )

        self.user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.check_password('Changed-password-456'))

    def test_logout_blacklists_refresh_token(self):
        refresh = self.authenticate()

        response = self.client.post(
            reverse('user:api-logout'),
            {'refresh': str(refresh)},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            BlacklistedToken.objects.filter(
                token__jti=refresh['jti'],
            ).exists()
        )

    def test_regular_user_cannot_list_all_users(self):
        self.authenticate()

        response = self.client.get(reverse('user:api-user-list'))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
