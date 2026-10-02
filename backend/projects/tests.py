from django.test import TestCase
from django.contrib.auth import get_user_model
from startups.models import StartupProfile
from .models import Project

User = get_user_model()

class ProjectModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="founder2@test.com",
            email="founder2@test.com", 
            role="startup"
        )
        self.startup = StartupProfile.objects.create(
            user=self.user,
            startup_name="FoodTech",
            industry="food"
        )
        self.project = Project.objects.create(
            startup=self.startup,
            project_title="Smart Packaging",
            project_description="Eco-friendly packaging",
            investment_sum=50000.00,
            project_stage="MVP"
        )

    def test_project_field_presence(self):
        """Verify presence of Project fields and their default values."""
        self.assertEqual(self.project.project_title, "Smart Packaging")
        self.assertEqual(self.project.investment_sum, 50000.00)
        self.assertEqual(self.project.raised_amount, 0)

    def test_foreign_key_relation_with_startup(self):
        """Verify ForeignKey relationship and related_name between StartupProfile and Project."""
        self.assertEqual(self.project.startup, self.startup)
        self.assertIn(self.project, self.startup.projects.all())

