from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test_user@example.com",
            email="test_user@example.com",
            first_name="Oleh",
            last_name="Test",
            role="startup",
            password="securepassword123"
        )

    def test_user_field_presence_and_values(self):
        """Verify presence and correctness of User model fields."""
        self.assertEqual(self.user.email, "test_user@example.com")
        self.assertEqual(self.user.username, "test_user@example.com")
        self.assertEqual(self.user.first_name, "Oleh")
        self.assertEqual(self.user.last_name, "Test")
        self.assertEqual(self.user.role, "startup")

    def test_role_methods(self):
        """Verify custom role validation methods."""
        self.assertTrue(self.user.can_have_startup_profile())
        self.assertFalse(self.user.can_have_investor_profile())

