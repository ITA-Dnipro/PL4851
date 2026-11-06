from unittest.mock import patch

import pytest
from django.db import IntegrityError
from django.test import TestCase

from projects.models import Project
from shared.slug_utils import (
    custom_slugify,
    generate_unique_slug,
    save_with_unique_slug,
)
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

    def test_unrelated_integrity_error_does_not_retry_when_slug_exists(self):
        startup = self._create_startup()
        Project.objects.create(
            startup=startup,
            project_title='Existing project',
            project_description='Description',
            investment_sum=100,
            slug='occupied',
        )
        project = Project(
            startup=startup,
            project_title='New project',
            project_description='Description',
            investment_sum=100,
        )
        save_calls = 0

        def fail_once():
            nonlocal save_calls
            save_calls += 1
            if save_calls == 1:
                raise IntegrityError('unrelated integrity failure')

        with (
            patch(
                'shared.slug_utils.generate_unique_slug',
                side_effect=['occupied', 'available'],
            ),
            self.assertRaises(IntegrityError),
        ):
            save_with_unique_slug(
                project,
                fail_once,
                project.project_title,
                Project.objects.all(),
                255,
                'project',
            )

        self.assertEqual(save_calls, 1)

    def test_slug_conflict_retries_are_limited(self):
        startup = self._create_startup()
        Project.objects.create(
            startup=startup,
            project_title='Existing project',
            project_description='Description',
            investment_sum=100,
            slug='occupied',
        )
        project = Project(
            startup=startup,
            project_title='New project',
            project_description='Description',
            investment_sum=100,
        )

        with (
            patch(
                'shared.slug_utils.generate_unique_slug', return_value='occupied'
            ) as generate_slug,
            self.assertRaises(IntegrityError),
        ):
            project.save()

        self.assertEqual(generate_slug.call_count, 4)

    def test_uses_queryset_database_for_slug_lookup_and_savepoint(self):
        project = Project(project_title='New project')
        queryset = Project.objects.using('replica')
        with (
            patch('shared.slug_utils.transaction.atomic') as atomic,
            patch(
                'shared.slug_utils.generate_unique_slug', return_value='new-project'
            ) as generate_slug,
        ):
            save_with_unique_slug(
                project,
                lambda: None,
                project.project_title,
                queryset,
                255,
                'project',
            )

        self.assertEqual(generate_slug.call_args.args[1].db, 'replica')
        self.assertEqual(atomic.call_args.kwargs, {'using': 'replica'})

    def _create_startup(self):
        from django.contrib.auth import get_user_model

        from startups.models import StartupProfile

        user = get_user_model().objects.create_user(
            email='slug-helper@test.com', role='startup'
        )
        return StartupProfile.objects.create(user=user, startup_name='Slug Helper')
