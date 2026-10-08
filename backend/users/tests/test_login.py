from datetime import timedelta
from unittest import mock

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APIRequestFactory, APITestCase
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from users.serializers.login import INVALID_CREDENTIALS_MESSAGE
from users.views.login import LOCKOUT_MESSAGE

pytestmark = pytest.mark.api

User = get_user_model()

LOGIN_URL = reverse('login')
EMAIL = 'founder@example.com'
PASSWORD = 'Str0ng-pass!'

# Lockout tests send more requests than the per-IP rate limit allows,
# so the limit is raised there to test the lockout on its own.
HIGH_RATE_LIMIT = mock.patch.object(
    ScopedRateThrottle, 'THROTTLE_RATES', {'login': '100/min'}
)


class LoginTestCase(APITestCase):
    def setUp(self):
        # Failed-attempt counters and throttling live in the cache
        cache.clear()
        self.user = User.objects.create_user(
            email=EMAIL,
            password=PASSWORD,
            first_name='Andrii',
            last_name='Test',
            role=User.Role.STARTUP,
        )

    def login(self, email=EMAIL, password=PASSWORD, **extra):
        return self.client.post(
            LOGIN_URL, {'email': email, 'password': password, **extra}, format='json'
        )


class LoginSuccessTests(LoginTestCase):
    def test_returns_tokens_and_user(self):
        response = self.login()

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(set(data), {'access', 'refresh', 'user'})
        self.assertEqual(
            data['user'],
            {'id': self.user.user_id, 'email': EMAIL, 'role': 'startup'},
        )

    def test_access_token_authenticates_the_user(self):
        access = self.login().json()['access']
        request = APIRequestFactory().get('/', HTTP_AUTHORIZATION=f'Bearer {access}')

        user, _ = JWTAuthentication().authenticate(request)

        self.assertEqual(user, self.user)

    def test_refresh_lifetime_is_default_without_remember(self):
        refresh = RefreshToken(self.login().json()['refresh'])

        lifetime = timedelta(seconds=refresh['exp'] - refresh['iat'])
        self.assertEqual(lifetime, settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'])

    def test_refresh_lifetime_is_longer_with_remember(self):
        refresh = RefreshToken(self.login(remember=True).json()['refresh'])

        lifetime = timedelta(seconds=refresh['exp'] - refresh['iat'])
        self.assertEqual(lifetime, settings.LOGIN_REMEMBER_REFRESH_LIFETIME)


class LoginFailureTests(LoginTestCase):
    def test_wrong_password_returns_401(self):
        response = self.login(password='wrong-password')

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'detail': INVALID_CREDENTIALS_MESSAGE})

    def test_unknown_email_returns_the_same_401(self):
        response = self.login(email='nobody@example.com')

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'detail': INVALID_CREDENTIALS_MESSAGE})

    def test_inactive_user_cannot_log_in(self):
        self.user.is_active = False
        self.user.save()

        response = self.login()

        self.assertEqual(response.status_code, 401)

    def test_invalid_payload_returns_400(self):
        cases = {
            'missing password': {'email': EMAIL},
            'missing email': {'password': PASSWORD},
            'invalid email': {'email': 'not-an-email', 'password': PASSWORD},
        }
        for name, payload in cases.items():
            with self.subTest(name):
                response = self.client.post(LOGIN_URL, payload, format='json')

                self.assertEqual(response.status_code, 400)


@HIGH_RATE_LIMIT
class LoginLockoutTests(LoginTestCase):
    def fail_max_attempts(self):
        for _ in range(settings.LOGIN_MAX_FAILED_ATTEMPTS):
            self.assertEqual(self.login(password='wrong-password').status_code, 401)

    def test_locks_account_after_too_many_failed_attempts(self):
        self.fail_max_attempts()

        # Even the correct password is rejected while the account is locked
        response = self.login()

        self.assertEqual(response.status_code, 429)
        # DRF appends "Expected available in N seconds." to the message
        self.assertTrue(response.json()['detail'].startswith(LOCKOUT_MESSAGE))
        self.assertEqual(response['Retry-After'], str(settings.LOGIN_LOCKOUT_SECONDS))

    def test_lockout_ignores_email_case(self):
        self.fail_max_attempts()

        response = self.login(email=EMAIL.upper())

        self.assertEqual(response.status_code, 429)

    def test_successful_login_resets_failed_attempts(self):
        for _ in range(settings.LOGIN_MAX_FAILED_ATTEMPTS - 1):
            self.login(password='wrong-password')

        self.assertEqual(self.login().status_code, 200)
        self.assertEqual(self.login(password='wrong-password').status_code, 401)
        self.assertEqual(self.login().status_code, 200)


class LoginRateLimitTests(LoginTestCase):
    def test_too_many_requests_from_one_ip_are_throttled(self):
        rate = ScopedRateThrottle.THROTTLE_RATES['login']
        max_requests = int(rate.split('/')[0])

        for _ in range(max_requests):
            self.assertEqual(self.login().status_code, 200)

        self.assertEqual(self.login().status_code, 429)
