from datetime import timedelta

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from ..admin import PasswordResetMetricsAdmin, PasswordResetTokenAdmin
from ..metrics import increment_metric
from ..models import PasswordResetMetrics, PasswordResetToken
from ..services import (
    consume_password_reset_token,
    create_password_reset_token,
    hash_token,
)

User = get_user_model()


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

    def test_new_token_revokes_previous_ones(self):
        create_password_reset_token(self.user)
        create_password_reset_token(self.user)

        tokens = self.user.password_reset_tokens
        self.assertEqual(tokens.filter(revoked=False).count(), 1)

    def test_previous_token_becomes_invalid_after_new_one(self):
        create_password_reset_token(self.user)

        self.token.refresh_from_db()
        self.assertFalse(self.token.is_valid())

    def test_inactive_user_token_is_invalid(self):
        self.user.is_active = False
        self.user.save(update_fields=['is_active'])

        self.assertFalse(self.token.is_valid())

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

    def test_successful_token_consumption_increments_confirms(self):
        raw_token = create_password_reset_token(self.user)

        result = consume_password_reset_token(raw_token)

        metrics = PasswordResetMetrics.objects.get(pk=1)

        self.assertIsNotNone(result)
        self.assertEqual(metrics.confirms, 1)

    def test_expired_token_increments_metric(self):
        raw_token = create_password_reset_token(self.user)

        token = PasswordResetToken.objects.get(token_hash=hash_token(raw_token))
        token.expires_at = timezone.now() - timedelta(minutes=1)
        token.save(update_fields=['expires_at'])

        result = consume_password_reset_token(raw_token)

        metrics = PasswordResetMetrics.objects.get(pk=1)

        self.assertIsNone(result)
        self.assertEqual(metrics.expired_attempts, 1)

    def test_reused_token_increments_metric(self):
        raw_token = create_password_reset_token(self.user)

        first_result = consume_password_reset_token(raw_token)
        second_result = consume_password_reset_token(raw_token)

        metrics = PasswordResetMetrics.objects.get(pk=1)

        self.assertIsNotNone(first_result)
        self.assertIsNone(second_result)
        self.assertEqual(metrics.reused_attempts, 1)


class PasswordResetMetricsTest(TestCase):
    def test_increment_requests(self):
        increment_metric('requests')

        metrics = PasswordResetMetrics.objects.get(pk=1)

        self.assertEqual(metrics.requests, 1)

    def test_increment_requests_multiple_times(self):
        increment_metric('requests')
        increment_metric('requests')
        increment_metric('requests')

        metrics = PasswordResetMetrics.objects.get(pk=1)

        self.assertEqual(metrics.requests, 3)
        self.assertEqual(PasswordResetMetrics.objects.count(), 1)

    def test_metrics_admin_permissions(self):
        metrics_admin = PasswordResetMetricsAdmin(
            PasswordResetMetrics,
            admin.site,
        )

        self.assertFalse(metrics_admin.has_add_permission(None))
        self.assertFalse(metrics_admin.has_delete_permission(None))
