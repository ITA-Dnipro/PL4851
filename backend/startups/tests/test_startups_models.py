import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from startups.models import Industry, LocationType, StartupFollower, StartupProfile

User = get_user_model()

pytestmark = pytest.mark.models


class StartupProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='founder@test.com',
            first_name='Ivan',
            last_name='Petrov',
            role='startup',
        )
        self.other_user = User.objects.create_user(
            email='other@test.com',
            first_name='Petro',
            last_name='Ivanov',
            role='startup',
        )
        self.industry = Industry.objects.get_or_create(
            slug='agriculture', defaults={'industry_name': 'Сільське господарство'}
        )[0]
        self.startup = StartupProfile.objects.create(
            user=self.user,
            startup_name='TechAgro',
            startup_description='AI for agriculture',
            startup_phone='+38 (099) 123-45-67',
            startup_email='info@techagro.co',
            location=LocationType.KYIV_CITY,
        )
        self.startup.industries.add(self.industry)

    def test_startup_field_presence(self):
        """Verify presence of StartupProfile fields and their default values."""
        self.assertEqual(self.startup.startup_name, 'TechAgro')
        self.assertTrue(self.startup.industries.filter(slug='agriculture').exists())
        self.assertEqual(self.startup.employees, 1)
        self.assertEqual(self.startup.location, LocationType.KYIV_CITY)

    def test_startup_phone_cleaning(self):
        """Verify save() strips non-digit characters from the phone number."""
        self.assertEqual(self.startup.startup_phone, '380991234567')

    def test_one_to_one_relation_with_user(self):
        """Verify OneToOne relationship between User and StartupProfile."""
        self.assertEqual(self.startup.user, self.user)
        self.assertEqual(self.user.startup_profile, self.startup)

    def test_employees_must_be_at_least_one(self):
        """Verify CheckConstraint blocks employees < 1."""
        with self.assertRaises(IntegrityError):
            StartupProfile.objects.create(
                user=self.other_user,
                startup_name='Zero',
                startup_description='D',
                startup_phone='1',
                startup_email='zero@test.com',
                employees=0,
            )

    def test_startup_email_normalization(self):
        """Verify save() normalizes startup_email to lowercase and strips whitespace."""
        startup_with_caps = StartupProfile.objects.create(
            user=self.other_user,
            startup_name='CleanMail',
            startup_description='Desc',
            startup_phone='123',
            startup_email='  Founder@TechAgro.CO  ',
        )
        self.assertEqual(startup_with_caps.startup_email, 'Founder@techagro.co')

    def test_slug_generation_and_transliteration(self):
        """Verify automatic transliteration of Ukrainian characters into a slug."""
        ukr_startup = StartupProfile.objects.create(
            user=self.other_user,
            startup_name='Гончарство та Ко',
            startup_description='Desc',
            startup_phone='123',
            startup_email='honchar@test.com',
        )
        self.assertEqual(ukr_startup.slug, 'honcharstvo-ta-ko')

    def test_slug_uniqueness_with_counter(self):
        """Verify slug uniqueness logic by appending a counter for duplicate names."""
        third_user = User.objects.create_user(
            email='third@test.com',
            first_name='Third',
            last_name='User',
            role='startup',
        )

        duplicate_startup = StartupProfile.objects.create(
            user=third_user,
            startup_name='TechAgro',
            startup_description='Desc',
            startup_phone='123',
            startup_email='techagro2@test.com',
        )
        self.assertEqual(duplicate_startup.slug, 'techagro-1')

    def test_slug_does_not_change_on_update(self):
        """Slug remains persistent, doesn't change when profile is updated."""
        ukr_startup = StartupProfile.objects.create(
            user=self.other_user,
            startup_name='Ромашка',
            startup_description='Desc',
            startup_phone='123',
            startup_email='romashka@test.com',
        )
        initial_slug = ukr_startup.slug
        ukr_startup.startup_name = 'Нова Назва Ромашки'
        ukr_startup.startup_phone = '0991112233'
        ukr_startup.save()
        self.assertEqual(ukr_startup.slug, initial_slug)

    def test_slug_fallback_for_special_characters(self):
        """Slug falls back to 'startup' if name contains only special characters."""
        special_startup = StartupProfile.objects.create(
            user=self.other_user,
            startup_name='!!!',
            startup_description='Desc',
            startup_phone='123',
            startup_email='special@test.com',
        )
        self.assertEqual(special_startup.slug, 'startup')

    def test_invalid_email_raises_validation_error(self):
        """Verify that full_clean() rejects an invalid email format."""
        invalid_startup = StartupProfile(
            user=self.other_user,
            startup_name='BadEmail',
            startup_description='Desc',
            startup_phone='123',
            startup_email='not-an-email-at-all',
        )
        with self.assertRaises(ValidationError):
            invalid_startup.full_clean()

    def test_startup_str_method(self):
        """Verify the __str__ method returns the startup name."""
        str_user = User.objects.create_user(
            email='str_user@test.com', first_name='S', last_name='U', role='startup'
        )
        startup = StartupProfile.objects.create(
            user=str_user,
            startup_name='Тестовий Стартап',
            startup_email='test_str@test.com',
        )
        self.assertEqual(str(startup), 'Тестовий Стартап')

    def test_exclude_pk_before_while_loop(self):
        """Verify works when updating an existing startup with empty slug."""
        update_user = User.objects.create_user(
            email='update_user@test.com', first_name='U', last_name='P', role='startup'
        )
        startup = StartupProfile.objects.create(
            user=update_user,
            startup_name='Оригінальний Назва',
            startup_email='orig@test.com',
        )
        startup.slug = ''
        startup.save()

        self.assertEqual(startup.slug, 'oryhinalnyy-nazva')

    def test_exclude_pk_inside_while_loop(self):
        """Verify works inside the while loop during collisions on update."""
        extra_user0 = User.objects.create_user(
            email='extra0@test.com', first_name='E0', last_name='L0', role='startup'
        )
        StartupProfile.objects.create(
            user=extra_user0, startup_name='Колізія', startup_email='first@test.com'
        )

        extra_user1 = User.objects.create_user(
            email='extra1@test.com', first_name='E1', last_name='L1', role='startup'
        )
        StartupProfile.objects.create(
            user=extra_user1, startup_name='Колізія', startup_email='second@test.com'
        )

        extra_user2 = User.objects.create_user(
            email='extra2@test.com', first_name='E2', last_name='L2', role='startup'
        )
        startup3 = StartupProfile.objects.create(
            user=extra_user2, startup_name='Інший', startup_email='third@test.com'
        )
        startup3.startup_name = 'Колізія'
        startup3.slug = ''
        startup3.save()

        self.assertEqual(startup3.slug, 'koliziya-2')

    def test_custom_slugify_empty_text_coverage(self):
        """Covers inside custom_slugify via empty startup_name."""
        extra_user3 = User.objects.create_user(
            email='extra3@test.com', first_name='E3', last_name='L3', role='startup'
        )
        startup_empty = StartupProfile.objects.create(
            user=extra_user3, startup_name='', startup_email='empty@test.com'
        )
        self.assertEqual(startup_empty.slug, 'startup')


class StartupFollowerModelTest(TestCase):
    def setUp(self):
        self.startup_user = User.objects.create_user(
            email='founder_f@test.com',
            first_name='Ivan',
            last_name='Petrov',
            role='startup',
        )
        self.investor_user = User.objects.create_user(
            email='investor_f@test.com',
            first_name='Petro',
            last_name='Investor',
            role='investor',
        )
        self.startup = StartupProfile.objects.create(
            user=self.startup_user,
            startup_name='FollowMe',
            startup_description='Desc',
            startup_phone='123',
            startup_email='follower_test@test.com',
        )

    def test_create_follower_success(self):
        """Verify that a user can successfully follow a startup."""
        follow = StartupFollower.objects.create(
            user=self.investor_user, startup=self.startup
        )
        self.assertEqual(follow.user, self.investor_user)
        self.assertEqual(follow.startup, self.startup)
        self.assertTrue(self.startup.followers.filter(pk=follow.pk).exists())

    def test_duplicate_follower_blocked_by_constraint(self):
        """UniqueConstraint prevents a user from following the same startup twice."""
        StartupFollower.objects.create(user=self.investor_user, startup=self.startup)

        with self.assertRaises(IntegrityError):
            StartupFollower.objects.create(
                user=self.investor_user, startup=self.startup
            )
