from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from users.models import PasswordResetToken
from users.views.password_reset_request import RESPONSE_DETAIL

User = get_user_model()
URL = '/api/auth/password-reset/'


class PasswordResetRequestTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='known@example.com',
            first_name='Known',
            last_name='User',
            role='startup',
            password='old_password123',
        )

    def request_reset(self, email, ip='10.0.0.1'):
        return self.client.post(URL, {'email': email}, format='json', REMOTE_ADDR=ip)

    def test_known_email_creates_token_and_sends_link(self):
        response = self.request_reset('known@example.com')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'detail': RESPONSE_DETAIL})
        self.assertEqual(self.user.password_reset_tokens.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('/reset-password?uid=', mail.outbox[0].body)
        self.assertIn('&token=', mail.outbox[0].body)

    def test_unknown_email_returns_same_response(self):
        response = self.request_reset('nobody@example.com')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'detail': RESPONSE_DETAIL})
        self.assertEqual(len(mail.outbox), 0)

    def test_ip_throttle(self):
        for i in range(5):
            self.request_reset(f'user{i}@example.com', ip='10.0.0.9')

        response = self.request_reset('another@example.com', ip='10.0.0.9')

        self.assertEqual(response.status_code, 429)

    def test_email_throttle(self):
        for i in range(5):
            self.request_reset('known@example.com', ip=f'10.0.1.{i}')

        response = self.request_reset('known@example.com', ip='10.0.1.99')

        self.assertEqual(response.status_code, 429)

    def test_old_expired_tokens_are_removed(self):
        PasswordResetToken.objects.create(
            user=self.user,
            token_hash='old',
            expires_at=timezone.now() - timedelta(days=8),
        )

        self.request_reset('known@example.com')

        self.assertFalse(PasswordResetToken.objects.filter(token_hash='old').exists())
