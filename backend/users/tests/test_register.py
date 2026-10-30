from urllib.parse import parse_qs, urlparse

import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.cache import cache
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from investors.models import InvestorProfile
from startups.models import StartupProfile
from users.serializers.register import PASSWORDS_DO_NOT_MATCH_MESSAGE
from users.services.email_verification import email_verification_token
from users.views.register import VERIFICATION_SENT_MESSAGE

pytestmark = pytest.mark.api

User = get_user_model()

REGISTER_URL = reverse('register')
LOGIN_URL = reverse('login')
EMAIL = 'founder@example.com'
PASSWORD = 'Str0ng-pass!'


def registration_data(**overrides):
    return {
        'email': EMAIL,
        'password': PASSWORD,
        'password_confirm': PASSWORD,
        'first_name': 'Andrii',
        'last_name': 'Test',
        'company_name': 'Ремесло Плюс',
        'role': User.Role.STARTUP,
        'legal_form': User.LegalForm.SOLE_PROPRIETOR,
        **overrides,
    }


class RegisterTestCase(APITestCase):
    def setUp(self):
        # Rate limiting lives in the cache
        cache.clear()

    def register(self, ip='127.0.0.1', **overrides):
        # The email is sent on commit, which a test transaction never reaches
        with self.captureOnCommitCallbacks(execute=True):
            return self.client.post(
                REGISTER_URL,
                registration_data(**overrides),
                format='json',
                REMOTE_ADDR=ip,
            )


class RegisterSuccessTests(RegisterTestCase):
    def test_returns_user_without_password(self):
        response = self.register()

        user = User.objects.get(email=EMAIL)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json(),
            {'id': user.pk, 'email': EMAIL, 'detail': VERIFICATION_SENT_MESSAGE},
        )

    def test_creates_inactive_user(self):
        self.register()

        user = User.objects.get(email=EMAIL)
        self.assertFalse(user.is_active)
        self.assertTrue(user.check_password(PASSWORD))
        self.assertEqual(user.first_name, 'Andrii')
        self.assertEqual(user.last_name, 'Test')
        self.assertEqual(user.role, User.Role.STARTUP)
        self.assertEqual(user.legal_form, User.LegalForm.SOLE_PROPRIETOR)

    def test_creates_startup_profile(self):
        self.register()

        profile = StartupProfile.objects.get(user__email=EMAIL)
        self.assertEqual(profile.startup_name, 'Ремесло Плюс')
        self.assertEqual(profile.slug, 'remeslo-plyus')
        self.assertEqual(profile.startup_description, '')
        self.assertEqual(profile.startup_email, '')
        self.assertFalse(InvestorProfile.objects.exists())

    def test_creates_investor_profile(self):
        self.register(role=User.Role.INVESTOR, company_name='Green Capital')

        profile = InvestorProfile.objects.get(user__email=EMAIL)
        self.assertEqual(profile.investor_name, 'Green Capital')
        self.assertEqual(profile.investor_type, '')
        self.assertFalse(StartupProfile.objects.exists())

    @override_settings(FRONTEND_URL='https://forum.example/')
    def test_sends_verification_link(self):
        self.register()

        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.to, [EMAIL])

        link = next(
            line for line in message.body.splitlines() if 'verify-email' in line
        )
        url = urlparse(link)
        self.assertEqual(f'{url.scheme}://{url.netloc}', 'https://forum.example')
        self.assertEqual(url.path, '/verify-email')
        self.assertEqual(set(parse_qs(url.query)), {'uid', 'token'})

    def test_stores_the_email_in_lowercase(self):
        response = self.register(email='Founder@EXAMPLE.com')

        self.assertEqual(response.json()['email'], EMAIL)
        self.assertTrue(User.objects.filter(email=EMAIL).exists())

    def test_user_cannot_log_in_before_verification(self):
        self.register()

        response = self.client.post(
            LOGIN_URL, {'email': EMAIL, 'password': PASSWORD}, format='json'
        )

        self.assertEqual(response.status_code, 401)


class RegisterDuplicateEmailTests(RegisterTestCase):
    def setUp(self):
        super().setUp()
        User.objects.create_user(
            email=EMAIL,
            password=PASSWORD,
            first_name='Existing',
            last_name='User',
            role=User.Role.INVESTOR,
        )

    def test_returns_409(self):
        response = self.register()

        self.assertEqual(response.status_code, 409)
        self.assertEqual(
            response.json(), {'detail': 'A user with this email already exists.'}
        )

    def test_ignores_case(self):
        response = self.register(email='FOUNDER@example.com')

        self.assertEqual(response.status_code, 409)

    def test_creates_nothing_and_sends_no_email(self):
        self.register()

        self.assertEqual(User.objects.count(), 1)
        self.assertFalse(StartupProfile.objects.exists())
        self.assertEqual(mail.outbox, [])


class RegisterUnverifiedEmailTests(RegisterTestCase):
    """A new registration replaces an account that never verified its email."""

    def setUp(self):
        super().setUp()
        self.register(password='First-pass1', password_confirm='First-pass1')
        self.pending = User.objects.get(email=EMAIL)
        self.old_token = email_verification_token.make_token(self.pending)
        mail.outbox.clear()

    def test_replaces_the_pending_account(self):
        response = self.register(
            role=User.Role.INVESTOR,
            company_name='Green Capital',
            email='FOUNDER@example.com',
        )

        self.assertEqual(response.status_code, 201)
        user = User.objects.get(email=EMAIL)
        self.assertNotEqual(user.pk, self.pending.pk)
        self.assertTrue(user.check_password(PASSWORD))
        self.assertEqual(user.role, User.Role.INVESTOR)
        self.assertFalse(StartupProfile.objects.exists())
        self.assertEqual(InvestorProfile.objects.get().user, user)

    def test_sends_a_new_link_and_the_old_one_stops_working(self):
        self.register()

        user = User.objects.get(email=EMAIL)
        self.assertEqual(len(mail.outbox), 1)
        self.assertFalse(email_verification_token.check_token(user, self.old_token))

    def test_keeps_an_account_deactivated_by_an_admin(self):
        # A user who has logged in before was verified, then deactivated
        self.pending.last_login = timezone.now()
        self.pending.save()

        response = self.register()

        self.assertEqual(response.status_code, 409)
        self.assertEqual(User.objects.get(email=EMAIL).pk, self.pending.pk)
        self.assertTrue(StartupProfile.objects.filter(user=self.pending).exists())


class RegisterValidationTests(RegisterTestCase):
    def assert_field_error(self, response, field):
        self.assertEqual(response.status_code, 400)
        self.assertIn(field, response.json())
        self.assertFalse(User.objects.exists())

    def test_requires_all_fields(self):
        response = self.client.post(REGISTER_URL, {}, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            set(response.json()),
            {
                'email',
                'password',
                'password_confirm',
                'first_name',
                'last_name',
                'company_name',
                'role',
                'legal_form',
            },
        )

    def test_rejects_different_passwords(self):
        response = self.register(password_confirm='Other-pass1')

        self.assert_field_error(response, 'password_confirm')
        self.assertEqual(
            response.json()['password_confirm'], [PASSWORDS_DO_NOT_MATCH_MESSAGE]
        )

    def test_rejects_password_without_digits(self):
        response = self.register(password='onlyletters', password_confirm='onlyletters')

        self.assert_field_error(response, 'password')

    def test_rejects_short_password(self):
        response = self.register(password='Ab1', password_confirm='Ab1')

        self.assert_field_error(response, 'password')

    def test_rejects_password_similar_to_email(self):
        response = self.register(
            password='founder@example.com1', password_confirm='founder@example.com1'
        )

        self.assert_field_error(response, 'password')

    def test_rejects_invalid_email(self):
        response = self.register(email='not-an-email')

        self.assert_field_error(response, 'email')

    def test_rejects_empty_role(self):
        response = self.register(role='')

        self.assert_field_error(response, 'role')

    def test_rejects_unknown_role(self):
        response = self.register(role='admin')

        self.assert_field_error(response, 'role')

    def test_rejects_unknown_legal_form(self):
        response = self.register(legal_form='corporation')

        self.assert_field_error(response, 'legal_form')

    def test_rejects_too_long_company_name(self):
        response = self.register(company_name='x' * 256)

        self.assert_field_error(response, 'company_name')


class RegisterRateLimitTests(RegisterTestCase):
    def test_limits_requests_per_ip(self):
        for _ in range(10):
            self.client.post(REGISTER_URL, {}, format='json', REMOTE_ADDR='10.0.0.1')

        response = self.register(ip='10.0.0.1')

        self.assertEqual(response.status_code, 429)
        self.assertIn('Retry-After', response.headers)
        self.assertFalse(User.objects.exists())

    def test_other_ip_is_not_limited(self):
        for _ in range(10):
            self.client.post(REGISTER_URL, {}, format='json', REMOTE_ADDR='10.0.0.1')

        response = self.register(ip='10.0.0.2')

        self.assertEqual(response.status_code, 201)
