import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from startups.models import StartupProfile

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
        self.startup = StartupProfile.objects.create(
            user=self.user,
            startup_name='TechAgro',
            startup_description='AI for agriculture',
            startup_phone='+38 (099) 123-45-67',
            industry='agriculture',
        )

    def test_startup_field_presence(self):
        """Verify presence of StartupProfile fields and their default values."""
        self.assertEqual(self.startup.startup_name, 'TechAgro')
        self.assertEqual(self.startup.industry, 'agriculture')
        self.assertEqual(self.startup.employees, 1)

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
