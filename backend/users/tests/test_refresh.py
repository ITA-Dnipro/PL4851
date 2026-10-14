from datetime import timedelta

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIRequestFactory, APITestCase
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

pytestmark = pytest.mark.api

User = get_user_model()

REFRESH_URL = reverse('refresh')


class RefreshTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='founder@example.com',
            password='Str0ng-pass!',
            first_name='Andrii',
            last_name='Test',
            role=User.Role.STARTUP,
        )
        self.refresh = RefreshToken.for_user(self.user)

    def post(self, refresh=None):
        if refresh is not None:
            self.client.cookies[settings.REFRESH_COOKIE_NAME] = refresh
        return self.client.post(REFRESH_URL)

    def test_returns_new_access_token(self):
        response = self.post(str(self.refresh))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.json()), {'access'})

    def test_new_access_token_authenticates_the_user(self):
        access = self.post(str(self.refresh)).json()['access']
        request = APIRequestFactory().get('/', HTTP_AUTHORIZATION=f'Bearer {access}')

        user, _ = JWTAuthentication().authenticate(request)

        self.assertEqual(user, self.user)

    def test_ignores_token_in_request_body(self):
        response = self.client.post(
            REFRESH_URL, {'refresh': str(self.refresh)}, format='json'
        )

        self.assertEqual(response.status_code, 401)

    def test_missing_cookie_returns_401(self):
        response = self.post()

        self.assertEqual(response.status_code, 401)

    def test_invalid_token_returns_401(self):
        response = self.post('not-a-token')

        self.assertEqual(response.status_code, 401)

    def test_expired_token_returns_401(self):
        self.refresh.set_exp(lifetime=-timedelta(seconds=1))

        response = self.post(str(self.refresh))

        self.assertEqual(response.status_code, 401)

    def test_access_token_instead_of_refresh_returns_401(self):
        response = self.post(str(self.refresh.access_token))

        self.assertEqual(response.status_code, 401)

    def test_inactive_user_returns_401(self):
        self.user.is_active = False
        self.user.save()

        response = self.post(str(self.refresh))

        self.assertEqual(response.status_code, 401)

    def test_deleted_user_returns_401(self):
        self.user.delete()

        response = self.post(str(self.refresh))

        self.assertEqual(response.status_code, 401)
