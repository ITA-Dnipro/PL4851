import pytest
from django.test import TestCase

from shared.slug_utils import custom_slugify, generate_unique_slug
from startups.models import Industry

pytestmark = pytest.mark.models


class SlugUtilsTest(TestCase):
    def test_custom_slugify_transliterates_ukrainian_text(self):
        self.assertEqual(custom_slugify('Щука та їжак'), 'shchuka-ta-yizhak')

    def test_custom_slugify_returns_empty_for_empty_text(self):
        self.assertEqual(custom_slugify(''), '')

    def test_generate_unique_slug_uses_fallback_and_counter(self):
        Industry.objects.create(slug='startup', industry_name='First')

        slug = generate_unique_slug('!!!', Industry.objects.all(), 20, 'startup')

        self.assertEqual(slug, 'startup-1')

    def test_generate_unique_slug_appends_counter_within_max_length(self):
        Industry.objects.create(slug='very-lon', industry_name='Existing')

        slug = generate_unique_slug(
            'Very Long Name', Industry.objects.all(), 8, 'startup'
        )

        self.assertEqual(slug, 'very-l-1')
        self.assertLessEqual(len(slug), 8)

    def test_generate_unique_slug_excludes_existing_object(self):
        industry = Industry.objects.create(slug='existing', industry_name='Existing')

        slug = generate_unique_slug(
            'Existing',
            Industry.objects.all(),
            20,
            'industry',
            exclude_pk=industry.pk,
        )

        self.assertEqual(slug, 'existing')
