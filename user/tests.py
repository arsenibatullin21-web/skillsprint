from django.test import TestCase
from django.urls import reverse

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
