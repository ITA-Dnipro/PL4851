import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
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
FOREIGN_ORIGIN = 'https://evil.example'


class TrustedOriginTests(APITestCase):
    def setUp(self):
        # Login throttling lives in the cache
        cache.clear()
        self.user = User.objects.create_user(
            email=EMAIL,
            password=PASSWORD,
            first_name='Andrii',
            last_name='Test',
            role=User.Role.STARTUP,
        )

    def login(self, origin):
        return self.client.post(
            LOGIN_URL,
            {'email': EMAIL, 'password': PASSWORD},
            format='json',
            HTTP_ORIGIN=origin,
        )

    def test_login_from_foreign_origin_returns_403_without_cookie(self):
        response = self.login(FOREIGN_ORIGIN)

        self.assertEqual(response.status_code, 403)
        self.assertNotIn(settings.REFRESH_COOKIE_NAME, response.cookies)

    def test_login_from_frontend_origin_works(self):
        response = self.login(settings.CORS_ALLOWED_ORIGINS[0])

        self.assertEqual(response.status_code, 200)

    def test_login_from_own_origin_works(self):
        # The browsable API sends the backend's own origin
        response = self.login('http://testserver')

        self.assertEqual(response.status_code, 200)

    def test_refresh_from_foreign_origin_returns_403(self):
        self.client.cookies[settings.REFRESH_COOKIE_NAME] = str(
            RefreshToken.for_user(self.user)
        )

        response = self.client.post(REFRESH_URL, HTTP_ORIGIN=FOREIGN_ORIGIN)

        self.assertEqual(response.status_code, 403)

    def test_logout_from_foreign_origin_keeps_the_cookie_and_token(self):
        self.client.cookies[settings.REFRESH_COOKIE_NAME] = str(
            RefreshToken.for_user(self.user)
        )

        response = self.client.post(LOGOUT_URL, HTTP_ORIGIN=FOREIGN_ORIGIN)

        self.assertEqual(response.status_code, 403)
        self.assertNotIn(settings.REFRESH_COOKIE_NAME, response.cookies)
        self.assertFalse(BlacklistedToken.objects.exists())
