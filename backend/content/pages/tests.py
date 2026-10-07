from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from content.pages.models import LandingPage
from content.sections.models import LandingBanner
from content.testing import create_admin_user

LANDING_URL = reverse('landing-content')

# Response key -> LandingPage flag that controls it, in the order of the page
BLOCK_FLAGS = {
    'hero': 'show_hero',
    'banner': 'show_banner',
    'for_whom': 'show_for_whom',
    'why_worth': 'show_why_worth',
}


class LandingContentViewTests(APITestCase):
    fixtures = ['landing']

    def test_returns_all_blocks_in_page_order(self):
        response = self.client.get(LANDING_URL)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.json()), list(BLOCK_FLAGS))

    def test_fixture_fills_every_block(self):
        data = self.client.get(LANDING_URL).json()

        self.assertTrue(data['hero']['hero_images'])
        self.assertTrue(data['banner']['title'])
        self.assertTrue(data['for_whom']['items'])
        self.assertTrue(data['why_worth']['items'])

    def test_hidden_block_is_null(self):
        for block, flag in BLOCK_FLAGS.items():
            with self.subTest(block=block):
                LandingPage.objects.update(**{flag: False})

                data = self.client.get(LANDING_URL).json()

                self.assertIsNone(data[block])
                for other_block in BLOCK_FLAGS.keys() - {block}:
                    self.assertIsNotNone(data[other_block])

                LandingPage.objects.update(**{flag: True})

    def test_missing_block_is_null(self):
        LandingBanner.objects.all().delete()

        data = self.client.get(LANDING_URL).json()

        self.assertIsNone(data['banner'])
        self.assertIsNotNone(data['hero'])

    def test_returns_404_without_landing_page(self):
        LandingPage.objects.all().delete()

        response = self.client.get(LANDING_URL)

        self.assertEqual(response.status_code, 404)


class LandingPageAdminTests(TestCase):
    fixtures = ['landing']

    def setUp(self):
        self.client.force_login(create_admin_user())

    def test_shows_visibility_flags_with_edit_links(self):
        response = self.client.get(
            reverse('admin:content_pages_landingpage_change', args=[1])
        )

        self.assertEqual(response.status_code, 200)
        for flag in BLOCK_FLAGS.values():
            self.assertContains(response, f'name="{flag}"')
        self.assertContains(
            response, reverse('admin:content_sections_landinghero_change', args=[1])
        )

    def test_unchecking_flag_hides_block(self):
        self.client.post(
            reverse('admin:content_pages_landingpage_change', args=[1]),
            {'show_hero': 'on', 'show_banner': 'on', 'show_why_worth': 'on'},
        )

        data = self.client.get(LANDING_URL).json()

        self.assertIsNone(data['for_whom'])
