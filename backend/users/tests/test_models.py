import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

User = get_user_model()

pytestmark = pytest.mark.models


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test_user@example.com',
            first_name='Oleh',
            last_name='Test',
            role='startup',
            password='securepassword123',
        )

    def test_user_field_presence_and_values(self):
        """Verify presence and correctness of User model fields."""
        self.assertEqual(self.user.email, 'test_user@example.com')
        self.assertEqual(self.user.first_name, 'Oleh')
        self.assertEqual(self.user.last_name, 'Test')
        self.assertEqual(self.user.role, 'startup')

    def test_role_methods(self):
        """Verify custom role validation methods."""
        self.assertTrue(self.user.can_have_startup_profile())
        self.assertFalse(self.user.can_have_investor_profile())

    def test_email_unique(self):
        """Verify email must be unique."""
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email='test_user@example.com',
                first_name='A',
                last_name='B',
                role='investor',
            )

    def test_password_is_hashed(self):
        """Verify the login identity is email."""
        self.assertTrue(self.user.check_password('securepassword123'))
        self.assertEqual(User.USERNAME_FIELD, 'email')
