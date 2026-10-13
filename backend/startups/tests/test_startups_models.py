import pytest
from django.contrib.auth import get_user_model
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
        )
        self.assertEqual(duplicate_startup.slug, 'techagro-1')

    def test_slug_does_not_change_on_update(self):
        """Slug remains persistent, doesn't change when profile is updated."""
        ukr_startup = StartupProfile.objects.create(
            user=self.other_user,
            startup_name='Ромашка',
            startup_description='Desc',
            startup_phone='123',
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
        )
        self.assertEqual(special_startup.slug, 'startup')


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
