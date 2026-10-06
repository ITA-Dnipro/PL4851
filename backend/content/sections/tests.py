from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from content.sections.models import (
    LandingBanner,
    LandingForWhomCard,
    LandingForWhomSection,
    LandingHero,
    LandingHeroImage,
    LandingWhyWorthItem,
    LandingWhyWorthSection,
)
from content.sections.serializers import (
    LandingBannerSerializer,
    LandingForWhomSectionSerializer,
    LandingHeroSerializer,
    LandingWhyWorthSectionSerializer,
)


class LandingHeroSerializerTests(TestCase):
    def setUp(self):
        self.hero = LandingHero.objects.create(
            title='FORUM',
            subtitle='Subtitle',
            cta_text='Join',
            cta_url='/about',
        )

    def test_structure(self):
        LandingHeroImage.objects.create(hero=self.hero, title='Wine', url='/wine.jpg')

        data = LandingHeroSerializer(self.hero).data

        self.assertEqual(
            data,
            {
                'title': 'FORUM',
                'subtitle': 'Subtitle',
                'cta_text': 'Join',
                'cta_url': '/about',
                'hero_images': [{'title': 'Wine', 'url': '/wine.jpg'}],
            },
        )

    def test_images_are_sorted_by_order(self):
        LandingHeroImage.objects.create(
            hero=self.hero, title='Second', url='/2', order=2
        )
        LandingHeroImage.objects.create(
            hero=self.hero, title='First', url='/1', order=1
        )

        images = LandingHeroSerializer(self.hero).data['hero_images']

        self.assertEqual([image['title'] for image in images], ['First', 'Second'])

    def test_without_images_returns_empty_list(self):
        data = LandingHeroSerializer(self.hero).data

        self.assertEqual(data['hero_images'], [])


class LandingBannerSerializerTests(TestCase):
    def test_structure(self):
        banner = LandingBanner.objects.create(
            title='Banner', cta_text='Join', cta_url='/register'
        )

        data = LandingBannerSerializer(banner).data

        self.assertEqual(
            data, {'title': 'Banner', 'cta_text': 'Join', 'cta_url': '/register'}
        )


class LandingForWhomSerializerTests(TestCase):
    def setUp(self):
        self.section = LandingForWhomSection.objects.create(title='For whom')

    def test_structure(self):
        LandingForWhomCard.objects.create(
            section=self.section, title='Startups', icon='rocket', description='Desc'
        )

        data = LandingForWhomSectionSerializer(self.section).data

        self.assertEqual(
            data,
            {
                'title': 'For whom',
                'items': [{'icon': 'rocket', 'title': 'Startups', 'desc': 'Desc'}],
            },
        )

    def test_items_are_sorted_by_order(self):
        LandingForWhomCard.objects.create(
            section=self.section, title='Second', icon='truck', order=2
        )
        LandingForWhomCard.objects.create(
            section=self.section, title='First', icon='rocket', order=1
        )

        items = LandingForWhomSectionSerializer(self.section).data['items']

        self.assertEqual([item['title'] for item in items], ['First', 'Second'])


class LandingWhyWorthSerializerTests(TestCase):
    def setUp(self):
        self.section = LandingWhyWorthSection.objects.create(title='Why worth')

    def test_structure(self):
        LandingWhyWorthItem.objects.create(
            section=self.section, title='Trends', description='Desc'
        )

        data = LandingWhyWorthSectionSerializer(self.section).data

        self.assertEqual(
            data,
            {'title': 'Why worth', 'items': [{'title': 'Trends', 'desc': 'Desc'}]},
        )

    def test_items_are_sorted_by_order(self):
        LandingWhyWorthItem.objects.create(
            section=self.section, title='Second', description='...', order=2
        )
        LandingWhyWorthItem.objects.create(
            section=self.section, title='First', description='...', order=1
        )

        items = LandingWhyWorthSectionSerializer(self.section).data['items']

        self.assertEqual([item['title'] for item in items], ['First', 'Second'])


class SectionSingletonAdminTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_superuser(
            username='admin', email='admin@example.com', password='admin'
        )
        self.client.force_login(user)

    def test_changelist_redirects_to_the_only_record(self):
        hero = LandingHero.objects.create(title='Hero')

        response = self.client.get(
            reverse('admin:content_sections_landinghero_changelist')
        )

        self.assertRedirects(
            response,
            reverse('admin:content_sections_landinghero_change', args=[hero.pk]),
        )

    def test_cannot_add_second_record(self):
        LandingHero.objects.create(title='Hero')

        response = self.client.get(reverse('admin:content_sections_landinghero_add'))

        self.assertEqual(response.status_code, 403)

    def test_can_add_record_when_missing(self):
        response = self.client.get(reverse('admin:content_sections_landinghero_add'))

        self.assertEqual(response.status_code, 200)

    def test_cannot_delete_record(self):
        hero = LandingHero.objects.create(title='Hero')

        response = self.client.get(
            reverse('admin:content_sections_landinghero_delete', args=[hero.pk])
        )

        self.assertEqual(response.status_code, 403)
