from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import PasswordResetMetrics, PasswordResetToken
from users.services import create_password_reset_token, hash_token

User = get_user_model()


class PasswordResetConfirmTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='reset_confirm@example.com',
            first_name='Reset',
            last_name='Confirm',
            role='startup',
            password='OldPassword123!',
        )
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = create_password_reset_token(self.user)
        self.url = '/api/auth/password-reset/confirm/'
        self.new_password = 'NewStrongPassword123!'

    def reset_password(self, token=None, password=None, uid=None):
        return self.client.post(
            self.url,
            {
                'uid': self.uid if uid is None else uid,
                'token': self.token if token is None else token,
                'password': (self.new_password if password is None else password),
            },
            format='json',
        )

    def test_password_reset_success(self):
        response = self.reset_password()

        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.new_password))

        token = PasswordResetToken.objects.get(
            token_hash=hash_token(self.token),
        )
        self.assertIsNotNone(token.used_at)

    def test_password_reset_invalid_token(self):
        response = self.reset_password(token='invalid-token')

        self.assertEqual(response.status_code, 400)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('OldPassword123!'))

    def test_password_reset_expired_token(self):
        token = PasswordResetToken.objects.get(
            token_hash=hash_token(self.token),
        )
        token.expires_at = timezone.now() - timedelta(seconds=1)
        token.save(update_fields=['expires_at'])

        response = self.reset_password()

        self.assertEqual(response.status_code, 400)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('OldPassword123!'))

    def test_password_reset_weak_password(self):
        response = self.reset_password(password='weak')

        self.assertEqual(response.status_code, 422)

        token = PasswordResetToken.objects.get(
            token_hash=hash_token(self.token),
        )
        self.assertIsNone(token.used_at)

    def test_password_reset_token_cannot_be_reused(self):
        first_response = self.reset_password()
        second_response = self.reset_password()

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 400)

    def test_password_reset_wrong_uid(self):
        other_user = User.objects.create_user(
            email='another_user@example.com',
            first_name='Another',
            last_name='User',
            role='investor',
            password='OldPassword123!',
        )
        wrong_uid = urlsafe_base64_encode(force_bytes(other_user.pk))

        response = self.reset_password(uid=wrong_uid)

        self.assertEqual(response.status_code, 400)

        self.user.refresh_from_db()
        other_user.refresh_from_db()

        self.assertTrue(self.user.check_password('OldPassword123!'))
        self.assertTrue(other_user.check_password('OldPassword123!'))

    def test_password_reset_blacklists_refresh_token(self):
        refresh_token = RefreshToken.for_user(self.user)

        response = self.reset_password()

        self.assertEqual(response.status_code, 200)

        with self.assertRaises(Exception):
            refresh_token.check_blacklist()

    def test_password_reset_audit_logging(self):
        with self.assertLogs(
            'users.views.password_reset_confirm',
            level='INFO',
        ) as captured:
            response = self.client.post(
                self.url,
                {
                    'uid': self.uid,
                    'token': self.token,
                    'password': self.new_password,
                },
                format='json',
                REMOTE_ADDR='192.0.2.10',
                HTTP_USER_AGENT='PasswordResetTest/1.0',
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(captured.records), 1)

        record = captured.records[0]

        self.assertEqual(record.event, 'password_reset_confirmed')
        self.assertEqual(record.user_id, self.user.pk)
        self.assertEqual(record.ip_address, '192.0.2.10')
        self.assertEqual(record.user_agent, 'PasswordResetTest/1.0')
        self.assertIsNotNone(record.timestamp)
        self.assertNotIn(self.new_password, record.getMessage())
        self.assertNotIn(self.token, record.getMessage())

    def test_password_reset_rollback_on_save_error(self):
        with patch.object(
            User,
            'save',
            side_effect=RuntimeError('Simulated database error'),
        ):
            with self.assertRaises(RuntimeError):
                self.reset_password()

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('OldPassword123!'))

        reset_token = PasswordResetToken.objects.get(
            token_hash=hash_token(self.token),
        )
        self.assertIsNone(reset_token.used_at)

        self.assertFalse(PasswordResetMetrics.objects.filter(confirms__gt=0).exists())

    def test_wrong_uid_does_not_consume_token(self):
        other_user = User.objects.create_user(
            email='wrong_uid@example.com',
            first_name='Wrong',
            last_name='User',
            role='investor',
            password='OldPassword123!',
        )

        wrong_uid = urlsafe_base64_encode(force_bytes(other_user.pk))

        invalid_response = self.reset_password(uid=wrong_uid)
        self.assertEqual(invalid_response.status_code, 400)

        reset_token = PasswordResetToken.objects.get(
            token_hash=hash_token(self.token),
        )
        self.assertIsNone(reset_token.used_at)

        valid_response = self.reset_password()
        self.assertEqual(valid_response.status_code, 200)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.new_password))

    def test_password_reset_missing_fields(self):
        response = self.client.post(
            self.url,
            {},
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('uid', response.data)
        self.assertIn('token', response.data)
        self.assertIn('password', response.data)

    def test_password_reset_invalid_uid_type(self):
        response = self.reset_password(uid=123)

        self.assertEqual(response.status_code, 400)
        self.assertIn('uid', response.data)

    def test_password_reset_invalid_token_type(self):
        response = self.reset_password(token=['invalid-token'])

        self.assertEqual(response.status_code, 400)
        self.assertIn('token', response.data)

    def test_password_reset_invalid_password_type(self):
        response = self.reset_password(password=['InvalidPassword123!'])

        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.data)

    def test_password_reset_null_fields(self):
        response = self.client.post(
            self.url,
            {
                'uid': None,
                'token': None,
                'password': None,
            },
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('uid', response.data)
        self.assertIn('token', response.data)
        self.assertIn('password', response.data)
