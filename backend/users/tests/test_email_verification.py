from datetime import timedelta
from unittest import mock

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.test import TestCase, override_settings

from users.services.email_verification import (
    EmailVerificationTokenGenerator,
    email_verification_token,
)

pytestmark = pytest.mark.models

User = get_user_model()


class EmailVerificationTokenTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='founder@example.com',
            password='Str0ng-pass!',
            first_name='Andrii',
            last_name='Test',
            role=User.Role.STARTUP,
            is_active=False,
        )
        self.token = email_verification_token.make_token(self.user)

    def test_new_token_is_valid(self):
        self.assertTrue(email_verification_token.check_token(self.user, self.token))

    def test_is_not_a_password_reset_token(self):
        self.assertFalse(default_token_generator.check_token(self.user, self.token))

    def test_stops_working_after_activation(self):
        self.user.is_active = True
        self.user.save()

        self.assertFalse(email_verification_token.check_token(self.user, self.token))

    def test_stops_working_after_email_change(self):
        self.user.email = 'new@example.com'
        self.user.save()

        self.assertFalse(email_verification_token.check_token(self.user, self.token))

    def test_belongs_to_one_user(self):
        other = User.objects.create_user(
            email='other@example.com',
            first_name='Other',
            last_name='User',
            role=User.Role.STARTUP,
            is_active=False,
        )

        self.assertFalse(email_verification_token.check_token(other, self.token))

    def test_rejects_broken_tokens(self):
        for token in ['', 'abc', f'{self.token}x', None]:
            with self.subTest(token=token):
                self.assertFalse(email_verification_token.check_token(self.user, token))

    @override_settings(EMAIL_VERIFICATION_TIMEOUT=60 * 60)
    def test_expires_after_the_timeout(self):
        generator = EmailVerificationTokenGenerator()
        now = generator._now()

        with mock.patch.object(
            generator, '_now', return_value=now + timedelta(minutes=59)
        ):
            self.assertTrue(generator.check_token(self.user, self.token))

        with mock.patch.object(
            generator, '_now', return_value=now + timedelta(minutes=61)
        ):
            self.assertFalse(generator.check_token(self.user, self.token))
