from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import InvestorProfile

User = get_user_model()

class InvestorProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="investor@test.com",
            email="investor@test.com",
            first_name="John",
            last_name="Rockefeller",
            role="investor"
        )
        self.investor = InvestorProfile.objects.create(
            user=self.user,
            investor_name="Rockefeller Corp",
            investor_type="company",
            investment_min=10000.00
        )

    def test_investor_field_presence(self):
        """Verify presence of InvestorProfile fields."""
        self.assertEqual(self.investor.investor_name, "Rockefeller Corp")
        self.assertEqual(self.investor.investor_type, "company")
        self.assertEqual(self.investor.investment_min, 10000.00)

    def test_relation_with_user(self):
        """Verify OneToOne relationship between User and InvestorProfile."""
        self.assertEqual(self.investor.user, self.user)
        self.assertEqual(self.user.investor_profile, self.investor)

