from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from investors.models import InvestorProfile
from projects.models import Project
from startups.models import StartupProfile

from .models import SavedProject

User = get_user_model()


class SavedProjectModelTest(TestCase):
    def setUp(self):
        self.user_startup = User.objects.create_user(
            username='s@test.com', email='s@test.com', role='startup'
        )
        self.user_investor = User.objects.create_user(
            username='i@test.com', email='i@test.com', role='investor'
        )
        self.startup = StartupProfile.objects.create(
            user=self.user_startup, startup_name='S1', industry='it'
        )
        self.investor = InvestorProfile.objects.create(
            user=self.user_investor, investor_name='I1', investor_type='private'
        )
        self.project = Project.objects.create(
            startup=self.startup,
            project_title='P1',
            project_description='D',
            investment_sum=1000,
            project_stage='Idea',
        )
        self.saved_project = SavedProject.objects.create(
            investor=self.investor, project=self.project
        )

    def test_saved_project_relations(self):
        """Verify ForeignKey relations and reverse related_name lookups."""
        self.assertEqual(self.saved_project.investor, self.investor)
        self.assertEqual(self.saved_project.project, self.project)
        self.assertIn(self.saved_project, self.investor.saved_projects.all())
        self.assertIn(self.saved_project, self.project.saved_by_investors.all())

    def test_duplicate_saved_project_rejected(self):
        with self.assertRaises(IntegrityError):
            SavedProject.objects.create(
                investor=self.investor,
                project=self.project,
            )
