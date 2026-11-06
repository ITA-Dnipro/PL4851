from datetime import timedelta
from unittest import mock

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import APITestCase

from users.services.email_verification import (
    EmailVerificationTokenGenerator,
    email_verification_token,
)
from users.views.verify_email import INVALID_LINK_MESSAGE, VERIFIED_MESSAGE

pytestmark = pytest.mark.api

User = get_user_model()

VERIFY_URL = reverse('verify-email')
LOGIN_URL = reverse('login')
EMAIL = 'founder@example.com'
PASSWORD = 'Craft-2026'


def uid_for(user):
    return urlsafe_base64_encode(force_bytes(user.pk))


class VerifyEmailTestCase(APITestCase):
    def setUp(self):
        # A registration waiting for verification
        self.user = User.objects.create_user(
            email=EMAIL,
            password=PASSWORD,
            first_name='Andrii',
            last_name='Test',
            role=User.Role.STARTUP,
            is_active=False,
            email_verified_at=None,
        )
        self.uid = uid_for(self.user)
        self.token = email_verification_token.make_token(self.user)

    def verify(self, uid=None, token=None):
        return self.client.post(
            VERIFY_URL,
            {'uid': uid or self.uid, 'token': token or self.token},
            format='json',
        )

    def assert_invalid_link(self, response):
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': INVALID_LINK_MESSAGE})
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        self.assertIsNone(self.user.email_verified_at)


class VerifyEmailSuccessTests(VerifyEmailTestCase):
    def test_activates_the_account(self):
        response = self.verify()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'detail': VERIFIED_MESSAGE})
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertIsNotNone(self.user.email_verified_at)

    def test_user_can_log_in_after_verification(self):
        self.verify()

        response = self.client.post(
            LOGIN_URL, {'email': EMAIL, 'password': PASSWORD}, format='json'
        )

        self.assertEqual(response.status_code, 200)

    def test_opening_the_link_again_is_not_an_error(self):
        self.verify()
        self.user.refresh_from_db()
        verified_at = self.user.email_verified_at

        response = self.verify()

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email_verified_at, verified_at)

    def test_does_not_activate_an_account_deactivated_by_an_admin(self):
        # Verified earlier, then deactivated: an old link must not undo that
        User.objects.filter(pk=self.user.pk).update(
            is_active=False, email_verified_at=self.user.date_joined
        )

        response = self.verify()

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)


class VerifyEmailInvalidLinkTests(VerifyEmailTestCase):
    def test_rejects_a_changed_token(self):
        self.assert_invalid_link(self.verify(token=f'{self.token[:-1]}x'))

    def test_rejects_another_users_token(self):
        other = User.objects.create_user(
            email='other@example.com',
            first_name='Other',
            last_name='User',
            role=User.Role.INVESTOR,
            is_active=False,
            email_verified_at=None,
        )

        self.assert_invalid_link(
            self.verify(token=email_verification_token.make_token(other))
        )

    def test_rejects_an_expired_token(self):
        later = EmailVerificationTokenGenerator()._now() + timedelta(hours=25)

        with mock.patch.object(
            EmailVerificationTokenGenerator, '_now', return_value=later
        ):
            response = self.verify()

        self.assert_invalid_link(response)

    def test_rejects_unknown_and_broken_uids(self):
        for uid in [urlsafe_base64_encode(b'999999'), '!!!', 'abc', 'MTI']:
            with self.subTest(uid=uid):
                self.assert_invalid_link(self.verify(uid=uid))

    def test_requires_uid_and_token(self):
        response = self.client.post(VERIFY_URL, {}, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(set(response.json()), {'uid', 'token'})
