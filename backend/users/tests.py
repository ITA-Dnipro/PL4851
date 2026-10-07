from datetime import timedelta

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from .admin import PasswordResetTokenAdmin
from .models import PasswordResetToken
from .services import (
    consume_password_reset_token,
    create_password_reset_token,
)

User = get_user_model()


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test_user@example.com',
            first_name='Oleh',
            last_name='Test',
            role='startup',
            password='securepassword123',
        )

    def test_user_field_presence_and_values(self):
        """Verify presence and correctness of User model fields."""
        self.assertEqual(self.user.email, 'test_user@example.com')
        self.assertEqual(self.user.first_name, 'Oleh')
        self.assertEqual(self.user.last_name, 'Test')
        self.assertEqual(self.user.role, 'startup')

    def test_role_methods(self):
        """Verify custom role validation methods."""
        self.assertTrue(self.user.can_have_startup_profile())
        self.assertFalse(self.user.can_have_investor_profile())

    def test_email_unique(self):
        """Verify email must be unique."""
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email='test_user@example.com',
                first_name='A',
                last_name='B',
                role='investor',
            )

    def test_password_is_hashed(self):
        """Verify the login identity is email."""
        self.assertTrue(self.user.check_password('securepassword123'))
        self.assertEqual(User.USERNAME_FIELD, 'email')


class PasswordResetTokenTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='reset_user@example.com',
            first_name='Reset',
            last_name='Test',
            role='startup',
            password='securepassword123',
        )

        self.token = PasswordResetToken.objects.create(
            user=self.user,
            token_hash='test-token-hash',
            expires_at=timezone.now() + timedelta(hours=1),
        )

    def test_token_is_valid(self):
        self.assertTrue(self.token.is_valid())

    def test_used_token_is_invalid(self):
        self.token.mark_as_used()

        self.assertIsNotNone(self.token.used_at)
        self.assertFalse(self.token.is_valid())

    def test_revoked_token_is_invalid(self):
        self.token.revoke()

        self.assertTrue(self.token.revoked)
        self.assertFalse(self.token.is_valid())

    def test_expired_token_is_invalid(self):
        self.token.expires_at = timezone.now() - timedelta(seconds=1)
        self.token.save(update_fields=['expires_at'])

        self.assertFalse(self.token.is_valid())

    def test_token_can_be_consumed_only_once(self):
        raw_token = create_password_reset_token(self.user)

        first_result = consume_password_reset_token(raw_token)
        second_result = consume_password_reset_token(raw_token)

        self.assertIsNotNone(first_result)
        self.assertIsNone(second_result)

    def test_invalid_token_returns_none(self):
        result = consume_password_reset_token('invalid-token')

        self.assertIsNone(result)

    def test_admin_can_revoke_token(self):
        token_admin = PasswordResetTokenAdmin(
            PasswordResetToken,
            admin.site,
        )
        token_admin.revoke_tokens(
            None,
            PasswordResetToken.objects.filter(pk=self.token.pk),
        )

        self.token.refresh_from_db()

        self.assertTrue(self.token.revoked)
        self.assertFalse(self.token.is_valid())
