from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from startups.serializers import StartupPublicProfileSerializer


class StartupProfileAPIViewTest(APITestCase):
    fixtures = [
        'fixtures/startups_projects_pagination_data.json',
        'fixtures/startup_profile_stats.json',
    ]

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

    def test_get_startups_list_success_coverage(self):
        """Verifies a successful list request"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_filtering_by_tag_industries_coverage(self):
        """Forcibly passes ?tag=craft to enter the `if tag` block:"""
        response = self.client.get(self.url, {'tag': 'craft'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class StartupPublicProfileDetailViewTest(APITestCase):
    fixtures = ['fixtures/startups_projects_pagination_data.json']

    def setUp(self):
        from startups.models import StartupProfile

        self.startup = StartupProfile.objects.first()
        if not self.startup:
            self.fail('Fixtures is empty')
        self.startup.is_verified = True
        self.startup.save()
        self.url = reverse(
            'startups:startup-detail', kwargs={'id': self.startup.startup_id}
        )

    def test_get_startup_profile_success(self):
        """Verification of a successful GET request for
        the detailed profile and field structure."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_fields = [
            'startup_id',
            'startup_name',
            'slug',
            'hero_image',
            'logo',
            'short_description',
            'about_html',
            'contact',
            'website',
            'industries',
            'followers_count',
            'projects_count',
            'created_at',
        ]
        for field in expected_fields:
            self.assertIn(field, response.data)

        self.assertIn('email', response.data['contact'])
        self.assertIn('phone', response.data['contact'])

    def test_get_unknown_startup_id_returns_404(self):
        """Verification that a request with a non-existent ID returns a 404."""
        invalid_url = reverse('startups:startup-detail', kwargs={'id': 99999})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_about_html_sanitization(self):
        """Checking that the HTML is being cleaned up"""
        self.startup.startup_description = (
            "Тест **Markdown** <script>alert('xss')</script>"
        )
        self.startup.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('<strong>Markdown</strong>', response.data['about_html'])
        self.assertNotIn('<script>', response.data['about_html'])

    def test_hero_image_fallback_placeholder(self):
        """Verify that the serializer returns a default
        placeholder if `hero_image` is empty."""
        from django.conf import settings

        old_media_url = settings.MEDIA_URL
        settings.MEDIA_URL = '/media/'
        try:
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(
                response.data['hero_image'], '/media/thumbs/hero.placeholder.jpg'
            )
        finally:
            settings.MEDIA_URL = old_media_url

    def test_logo_and_hero_image_urls_when_exist(self):
        """Verifies behavior when images are loaded"""
        from django.core.files.uploadedfile import SimpleUploadedFile

        fake_image = SimpleUploadedFile(
            'test.jpg', b'file_content', content_type='image/jpeg'
        )
        self.startup.logo = fake_image
        self.startup.hero_image = fake_image
        self.startup.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('test', response.data['logo'])
        self.assertIn('test', response.data['hero_image'])

    def test_about_html_empty_description_fallback(self):
        """Verifies an empty string is returned if there is no description."""
        self.startup.startup_description = ''
        self.startup.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['about_html'], '')

    def test_projects_count_fallback_without_annotate(self):
        """invokes the serializer without an annotation, triggering the else-block"""
        from startups.models import StartupProfile

        raw_startup = StartupProfile.objects.get(pk=self.startup.startup_id)
        serializer = StartupPublicProfileSerializer(raw_startup)
        self.assertEqual(serializer.data['projects_count'], 7)
