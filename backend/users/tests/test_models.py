import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
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

    def test_superuser_has_no_role(self):
        """Verify a superuser is neither a startup nor an investor."""
        admin = User.objects.create_superuser(
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            password='securepassword123',
        )

        self.assertEqual(admin.role, '')
        self.assertFalse(admin.can_have_startup_profile())
        self.assertFalse(admin.can_have_investor_profile())

    def test_email_is_stored_in_lowercase(self):
        """Verify create_user lowercases the whole email."""
        user = User.objects.create_user(
            email='Mixed.Case@Example.COM',
            first_name='A',
            last_name='B',
            role='investor',
        )

        self.assertEqual(user.email, 'mixed.case@example.com')

    def test_email_unique_ignores_case(self):
        """Verify the database rejects an email that differs only by case."""
        with self.assertRaises(IntegrityError):
            User.objects.create(
                email='Test_User@example.com',
                first_name='A',
                last_name='B',
                role='investor',
            )

    def test_clean_lowercases_email(self):
        """Verify forms (e.g. the admin) save the email in lowercase."""
        user = User(
            email='New.User@Example.com',
            first_name='A',
            last_name='B',
            role='investor',
        )
        user.set_unusable_password()

        user.full_clean()

        self.assertEqual(user.email, 'new.user@example.com')

    def test_full_clean_rejects_email_differing_by_case(self):
        """Verify forms report a case-only duplicate instead of a database error."""
        user = User(
            email='TEST_USER@example.com',
            first_name='A',
            last_name='B',
            role='investor',
        )
        user.set_unusable_password()

        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_users_count_as_verified_by_default(self):
        """Verify accounts created outside registration don't wait for verification."""
        self.assertIsNotNone(self.user.email_verified_at)
