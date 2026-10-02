from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import StartupProfile

User = get_user_model()

class StartupProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="founder@test.com",
            email="founder@test.com",
            first_name="Ivan",
            last_name="Petrov",
            role="startup"
        )
        self.startup = StartupProfile.objects.create(
            user=self.user,
            startup_name="TechAgro",
            startup_description="AI for agriculture",
            startup_phone="+38 (099) 123-45-67",
            industry="agriculture"
        )

    def test_startup_field_presence(self):
        """Verify presence of StartupProfile fields and their default values."""
        self.assertEqual(self.startup.startup_name, "TechAgro")
        self.assertEqual(self.startup.industry, "agriculture")
        self.assertEqual(self.startup.employees, 1)

    def test_startup_phone_cleaning(self):
        """Verify that save() method strips non-digit characters from the phone number."""
        self.assertEqual(self.startup.startup_phone, "380991234567")

    def test_one_to_one_relation_with_user(self):
        """Verify OneToOne relationship between User and StartupProfile."""
        self.assertEqual(self.startup.user, self.user)
        self.assertEqual(self.user.startup_profile, self.startup)

