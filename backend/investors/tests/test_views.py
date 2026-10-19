import pytest
from django.urls import reverse
from rest_framework.test import APITestCase

pytestmark = pytest.mark.api

LIST_URL = reverse('investors:investor-list')

# Investors from the fixture
GREEN_CAPITAL = 31  # verified fund with all fields filled
OLENA = 32  # verified private investor with empty optional fields
CRAFT_VENTURES = 33  # not verified


def detail_url(investor_id):
    return reverse('investors:investor-detail', kwargs={'id': investor_id})


def result_ids(response):
    return [item['investor_id'] for item in response.json()['results']]


class InvestorProfileListViewTest(APITestCase):
    fixtures = ['investors']

    def test_lists_only_verified_investors(self):
        response = self.client.get(LIST_URL)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)
        self.assertEqual(result_ids(response), [GREEN_CAPITAL, OLENA])

    def test_returns_card_fields(self):
        response = self.client.get(LIST_URL)

        self.assertEqual(
            response.json()['results'][0],
            {
                'investor_id': GREEN_CAPITAL,
                'investor_name': 'Green Capital',
                'investor_type': 'fund',
                'investment_min': '50000.00',
            },
        )

    def test_paginates_with_page_size(self):
        response = self.client.get(LIST_URL, {'page_size': 1})

        data = response.json()
        self.assertEqual(data['count'], 2)
        self.assertEqual(result_ids(response), [GREEN_CAPITAL])
        self.assertIsNotNone(data['next'])

    def test_searches_by_name(self):
        response = self.client.get(LIST_URL, {'search': 'green'})

        self.assertEqual(result_ids(response), [GREEN_CAPITAL])

    def test_filters_by_type(self):
        response = self.client.get(LIST_URL, {'type': 'private'})

        self.assertEqual(result_ids(response), [OLENA])

    def test_unknown_type_returns_empty_list(self):
        response = self.client.get(LIST_URL, {'type': 'bank'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(result_ids(response), [])


class InvestorProfileDetailViewTest(APITestCase):
    fixtures = ['investors']

    def test_returns_full_profile(self):
        response = self.client.get(detail_url(GREEN_CAPITAL))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'investor_id': GREEN_CAPITAL,
                'investor_name': 'Green Capital',
                'investor_type': 'fund',
                'investor_description': (
                    'We invest in craft food and eco packaging.\n'
                    'Seed rounds and mentorship for small producers.'
                ),
                'contact': {'phone': '+380501234567'},
                'investment_min': '50000.00',
                'is_verified': True,
            },
        )

    def test_returns_empty_optional_fields(self):
        response = self.client.get(detail_url(OLENA))

        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['investor_description'], '')
        self.assertEqual(data['contact'], {'phone': ''})
        self.assertIsNone(data['investment_min'])

    def test_unverified_investor_returns_404(self):
        response = self.client.get(detail_url(CRAFT_VENTURES))

        self.assertEqual(response.status_code, 404)

    def test_unknown_investor_returns_404(self):
        response = self.client.get(detail_url(999))

        self.assertEqual(response.status_code, 404)
