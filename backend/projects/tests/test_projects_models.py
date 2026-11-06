import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from projects.models import Project, ProjectAttachment, ProjectAudit
from startups.models import Industry, LocationType, StartupProfile

User = get_user_model()

pytestmark = pytest.mark.models


class ProjectModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='founder2@test.com', role='startup')
        self.startup = StartupProfile.objects.create(
            user=self.user, startup_name='FoodTech', location=LocationType.KYIV_CITY
        )
        self.industry = Industry.objects.get_or_create(
            slug='food', defaults={'industry_name': 'Їжа / Харчова промисловість'}
        )[0]
        self.startup.industries.add(self.industry)
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

    def test_project_defaults_and_unique_slug(self):
        project = Project.objects.create(
            startup=self.startup,
            project_title='Новий проєкт',
            project_description='Description',
            investment_sum=100,
        )
        duplicate = Project.objects.create(
            startup=self.startup,
            project_title='Новий проєкт',
            project_description='Description',
            investment_sum=100,
        )

        self.assertEqual(project.slug, 'novyy-proyekt')
        self.assertEqual(duplicate.slug, 'novyy-proyekt-1')
        self.assertEqual(project.project_stage, 'idea')
        self.assertEqual(project.currency, 'UAH')
        self.assertEqual(project.visibility, Project.Visibility.PUBLIC)
        self.assertFalse(project.industries.exists())

    def test_project_industries_relation(self):
        self.project.industries.add(self.industry)

        self.assertIn(self.project, self.industry.projects.all())

    def test_project_attachment_and_audit_relations(self):
        attachment = ProjectAttachment.objects.create(
            project=self.project,
            type=ProjectAttachment.AttachmentType.PDF,
            caption='Pitch deck',
        )
        audit = ProjectAudit.objects.create(
            project=self.project,
            user=self.user,
            changes={'status': ['draft', 'active']},
        )

        self.assertIn(attachment, self.project.attachments.all())
        self.assertEqual(attachment.order, 0)
        self.assertEqual(audit.changes, {'status': ['draft', 'active']})
        self.assertIn(audit, self.project.audit_events.all())

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
