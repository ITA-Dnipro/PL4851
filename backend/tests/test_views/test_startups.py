from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class StartupProfileAPIViewTest(APITestCase):
    fixtures = ['fixtures/startups_pagination_data.json']

    def setUp(self):
        self.url = reverse('startups:startup-list')

    def tearDown(self):
        super().tearDown()

    def test_get_startups_list_success(self):
        """Verify GET /api/startups/ returns 200 and matches expected structure."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)

        self.assertTrue(len(response.data['results']) <= 8)

        first_startup = response.data['results'][0]
        self.assertIn('startup_id', first_startup)
        self.assertIn('startup_name', first_startup)
        self.assertIn('short_description', first_startup)
        self.assertIn('logo', first_startup)
        self.assertIn('location', first_startup)
        self.assertIn('industries', first_startup)

    def test_pagination_limits_and_splits_items_correctly(self):
        """Verify pagination limits first page to 8 and provides next link."""
        response = self.client.get(self.url)

        self.assertEqual(len(response.data['results']), 8)
        self.assertIsNotNone(response.data['next'])

    def test_filtering_by_tag_industries(self):
        """Verify that filtering returns only startups matching the industry slug."""
        response = self.client.get(self.url, {'tag': 'craft'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for startup in response.data['results']:
            self.assertIn('Ремесла', startup['industries'])

    def test_search_by_startup_name(self):
        """Verify that searching filters records accurately by startup name."""
        response = self.client.get(self.url, {'search': 'Handmade'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['startup_name'], 'Handmade Co')
