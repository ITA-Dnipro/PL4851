import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from projects.models import Project
from startups.models import StartupProfile

User = get_user_model()

pytestmark = pytest.mark.models


class ProjectModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='founder2@test.com', role='startup')
        self.startup = StartupProfile.objects.create(
            user=self.user, startup_name='FoodTech', industry='food'
        )
        self.project = Project.objects.create(
            startup=self.startup,
            project_title='Smart Packaging',
            project_description='Eco-friendly packaging',
            investment_sum=50000.00,
            project_stage='MVP',
        )

    def test_project_field_presence(self):
        """Verify presence of Project fields and their default values."""
        self.assertEqual(self.project.project_title, 'Smart Packaging')
        self.assertEqual(self.project.investment_sum, 50000.00)
        self.assertEqual(self.project.raised_amount, 0)

    def test_foreign_key_relation_with_startup(self):
        """Verify ForeignKey relationship and related_name with StartupProfile."""
        self.assertEqual(self.project.startup, self.startup)
        self.assertIn(self.project, self.startup.projects.all())

    def test_investment_sum_must_be_positive(self):
        """Verify CheckConstraint blocks investment_sum <= 0."""
        with self.assertRaises(IntegrityError):
            Project.objects.create(
                startup=self.startup,
                project_title='Zero',
                project_description='D',
                investment_sum=0,
                project_stage='Idea',
            )

    def test_raised_amount_cannot_be_negative(self):
        """Verify CheckConstraint blocks negative raised_amount."""
        with self.assertRaises(IntegrityError):
            Project.objects.create(
                startup=self.startup,
                project_title='Project',
                project_description='D',
                investment_sum=100,
                project_stage='Idea',
                raised_amount=-1,
            )
