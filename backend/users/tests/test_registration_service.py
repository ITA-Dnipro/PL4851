from unittest import mock

import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.db import IntegrityError
from django.test import TestCase

from startups.models import StartupProfile
from users.exceptions import EmailAlreadyRegistered
from users.services.registration import register_user

pytestmark = pytest.mark.models

User = get_user_model()

USER_DATA = {
    'email': 'founder@example.com',
    'password': 'Str0ng-pass!',
    'first_name': 'Andrii',
    'last_name': 'Test',
    'company_name': 'Handmade Co',
    'role': User.Role.STARTUP,
    'legal_form': User.LegalForm.LEGAL_ENTITY,
}


class RegisterUserTests(TestCase):
    def test_rolls_back_the_user_when_the_profile_fails(self):
        with mock.patch.object(
            StartupProfile.objects, 'create', side_effect=IntegrityError
        ):
            with self.assertRaises(IntegrityError):
                register_user(**USER_DATA)

        self.assertFalse(User.objects.exists())

    def test_email_taken_after_the_serializer_check(self):
        # Another request saved the same email between validation and saving
        User.objects.create_user(
            email=USER_DATA['email'],
            first_name='Other',
            last_name='User',
            role=User.Role.INVESTOR,
        )

        with self.assertRaises(EmailAlreadyRegistered):
            register_user(**USER_DATA)

        self.assertEqual(User.objects.count(), 1)
        self.assertFalse(StartupProfile.objects.exists())

    def test_sends_the_email_only_after_commit(self):
        with self.captureOnCommitCallbacks() as callbacks:
            register_user(**USER_DATA)

            self.assertEqual(mail.outbox, [])

        for callback in callbacks:
            callback()
        self.assertEqual(len(mail.outbox), 1)

    def test_email_failure_keeps_the_user_and_is_logged(self):
        with mock.patch(
            'users.services.email_verification.send_mail',
            side_effect=OSError('SMTP server is down'),
        ):
            with self.assertLogs('users.services.email_verification', 'ERROR'):
                with self.captureOnCommitCallbacks(execute=True):
                    register_user(**USER_DATA)

        self.assertTrue(User.objects.filter(email=USER_DATA['email']).exists())
