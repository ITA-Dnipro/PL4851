from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from .models import InvestorProfile

User = get_user_model()


class InvestorProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='investor@test.com',
            first_name='John',
            last_name='Rockefeller',
            role='investor',
        )
        self.other_user = User.objects.create_user(
            email='other@test.com',
            first_name='Petro',
            last_name='Ivanov',
            role='investor',
        )
        self.investor = InvestorProfile.objects.create(
            user=self.user,
            investor_name='Rockefeller Corp',
            investor_type='company',
            investment_min=10000.00,
        )

    def test_investor_field_presence(self):
        """Verify presence of InvestorProfile fields."""
        self.assertEqual(self.investor.investor_name, 'Rockefeller Corp')
        self.assertEqual(self.investor.investor_type, 'company')
        self.assertEqual(self.investor.investment_min, 10000.00)

    def test_relation_with_user(self):
        """Verify OneToOne relationship between User and InvestorProfile."""
        self.assertEqual(self.investor.user, self.user)
        self.assertEqual(self.user.investor_profile, self.investor)

    def test_negative_investment_min_rejected(self):
        """Verify CheckConstraint blocks negative investment_min."""
        with self.assertRaises(IntegrityError):
            InvestorProfile.objects.create(
                user=self.other_user,
                investor_name='Bad',
                investor_type='fund',
                investment_min=-1,
            )

    def test_edrpou_unique(self):
        """Verify edrpou_or_ipn must be unique."""
        self.investor.edrpou_or_ipn = '12345678'
        self.investor.save()
        with self.assertRaises(IntegrityError):
            InvestorProfile.objects.create(
                user=self.other_user,
                investor_name='Duplicate',
                investor_type='fund',
                edrpou_or_ipn='12345678',
            )
