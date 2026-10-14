import pytest
from django.urls import reverse
from rest_framework.test import APITestCase

pytestmark = pytest.mark.api


class HealthViewTests(APITestCase):
    def test_returns_ok(self):
        response = self.client.get(reverse('health'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok'})
