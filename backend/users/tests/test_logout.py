from datetime import timedelta
from unittest import mock

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.management import call_command
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken

pytestmark = pytest.mark.api

User = get_user_model()

LOGIN_URL = reverse('login')
LOGOUT_URL = reverse('logout')
REFRESH_URL = reverse('refresh')
EMAIL = 'founder@example.com'
PASSWORD = 'Str0ng-pass!'


class LogoutTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email=EMAIL,
            password=PASSWORD,
            first_name='Andrii',
            last_name='Test',
            role=User.Role.STARTUP,
        )
        self.refresh = str(RefreshToken.for_user(self.user))

    def set_cookie(self, refresh):
        self.client.cookies[settings.REFRESH_COOKIE_NAME] = refresh

    def assert_cookie_deleted(self, response):
        cookie = response.cookies[settings.REFRESH_COOKIE_NAME]
        self.assertEqual(cookie.value, '')
        self.assertEqual(cookie['path'], settings.REFRESH_COOKIE_PATH)
        self.assertEqual(cookie['max-age'], 0)

    def test_returns_204_revokes_the_token_and_deletes_the_cookie(self):
        self.set_cookie(self.refresh)

        response = self.client.post(LOGOUT_URL)

        self.assertEqual(response.status_code, 204)
        self.assert_cookie_deleted(response)
        jti = RefreshToken(self.refresh, verify=False)['jti']
        self.assertTrue(BlacklistedToken.objects.filter(token__jti=jti).exists())

    def test_refresh_after_logout_returns_401(self):
        self.set_cookie(self.refresh)
        self.client.post(LOGOUT_URL)
        self.set_cookie(self.refresh)

        response = self.client.post(REFRESH_URL)

        self.assertEqual(response.status_code, 401)

    def test_repeated_logout_still_returns_204(self):
        self.set_cookie(self.refresh)
        self.client.post(LOGOUT_URL)
        self.set_cookie(self.refresh)

        response = self.client.post(LOGOUT_URL)

        self.assertEqual(response.status_code, 204)
        self.assert_cookie_deleted(response)

    def test_invalid_token_still_returns_204_and_deletes_the_cookie(self):
        self.set_cookie('not-a-token')

        response = self.client.post(LOGOUT_URL)

        self.assertEqual(response.status_code, 204)
        self.assert_cookie_deleted(response)

    def test_missing_cookie_returns_204(self):
        response = self.client.post(LOGOUT_URL)

        self.assertEqual(response.status_code, 204)

    def test_remember_token_stays_revoked_after_flushing_expired_tokens(self):
        # Login throttling lives in the cache
        cache.clear()
        login = self.client.post(
            LOGIN_URL,
            {'email': EMAIL, 'password': PASSWORD, 'remember': True},
            format='json',
        )
        refresh = login.cookies[settings.REFRESH_COOKIE_NAME].value
        self.client.post(LOGOUT_URL)

        # A day later the default refresh lifetime is over, the remember one isn't
        a_day_later = timezone.now() + timedelta(days=1, minutes=1)
        with mock.patch(
            'rest_framework_simplejwt.token_blacklist.management.commands'
            '.flushexpiredtokens.aware_utcnow',
            return_value=a_day_later,
        ):
            call_command('flushexpiredtokens')
        self.set_cookie(refresh)

        response = self.client.post(REFRESH_URL)

        self.assertEqual(response.status_code, 401)
