from urllib.parse import parse_qs, urlparse

import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APITestCase

from users.services.email_verification import email_verification_token, user_from_uid
from users.views.resend_verification import RESENT_MESSAGE

pytestmark = pytest.mark.api

User = get_user_model()

RESEND_URL = reverse('resend-verification')
PENDING_EMAIL = 'pending@example.com'
VERIFIED_EMAIL = 'verified@example.com'


class ResendVerificationTestCase(APITestCase):
    def setUp(self):
        # Rate limiting lives in the cache
        cache.clear()
        self.pending = User.objects.create_user(
            email=PENDING_EMAIL,
            first_name='Pending',
            last_name='User',
            role=User.Role.STARTUP,
            is_active=False,
            email_verified_at=None,
        )
        User.objects.create_user(
            email=VERIFIED_EMAIL,
            first_name='Verified',
            last_name='User',
            role=User.Role.INVESTOR,
        )

    def resend(self, email, ip='127.0.0.1'):
        # The email is sent on commit, which a test transaction never reaches
        with self.captureOnCommitCallbacks(execute=True):
            return self.client.post(
                RESEND_URL, {'email': email}, format='json', REMOTE_ADDR=ip
            )


class ResendVerificationTests(ResendVerificationTestCase):
    def test_sends_a_working_link_to_a_pending_registration(self):
        response = self.resend(PENDING_EMAIL)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'detail': RESENT_MESSAGE})
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [PENDING_EMAIL])

        link = next(
            line for line in mail.outbox[0].body.splitlines() if 'verify-email' in line
        )
        query = parse_qs(urlparse(link).query)
        user = user_from_uid(query['uid'][0])
        self.assertEqual(user, self.pending)
        self.assertTrue(email_verification_token.check_token(user, query['token'][0]))

    def test_ignores_the_email_case(self):
        self.resend('Pending@EXAMPLE.com')

        self.assertEqual(mail.outbox[0].to, [PENDING_EMAIL])

    def test_same_answer_without_an_email_for_other_addresses(self):
        for email in [VERIFIED_EMAIL, 'nobody@example.com']:
            with self.subTest(email=email):
                response = self.resend(email)

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), {'detail': RESENT_MESSAGE})
        self.assertEqual(mail.outbox, [])

    def test_rejects_an_invalid_email(self):
        response = self.resend('not-an-email')

        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.json())

    def test_rejects_a_body_that_is_not_an_object(self):
        response = self.client.post(RESEND_URL, ['a'], format='json')

        self.assertEqual(response.status_code, 400)


class ResendVerificationRateLimitTests(ResendVerificationTestCase):
    def test_limits_letters_to_one_address_from_any_client(self):
        for i in range(3):
            self.resend(PENDING_EMAIL, ip=f'10.0.0.{i}')

        response = self.resend('PENDING@example.com', ip='10.0.0.9')

        self.assertEqual(response.status_code, 429)
        self.assertIn('Retry-After', response.headers)
        self.assertEqual(len(mail.outbox), 3)

    def test_case_variants_of_an_address_share_the_limit(self):
        # PostgreSQL matches the dotless "ı" to "i" in iexact, like upper() does
        variants = ['pending@example.com', 'PENDING@example.com', 'pendıng@example.com']
        for i, email in enumerate(variants):
            self.resend(email, ip=f'10.0.2.{i}')

        response = self.resend(PENDING_EMAIL, ip='10.0.2.9')

        self.assertEqual(response.status_code, 429)

    def test_limits_requests_from_one_client(self):
        for i in range(5):
            self.resend(f'user{i}@example.com', ip='10.0.1.1')

        response = self.resend(PENDING_EMAIL, ip='10.0.1.1')

        self.assertEqual(response.status_code, 429)
        self.assertEqual(mail.outbox, [])
