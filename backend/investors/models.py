from django.db import models

class InvestorProfile(models.Model):
    class InvestorType(models.TextChoices):
        PRIVATE = "private", "Private"
        FUND = "fund", "Fund"
        COMPANY = "company", "Company"

    investor_id = models.AutoField(primary_key=True)
    user = models.OneToOneField("users.User", on_delete=models.RESTRICT, related_name="investor_profile")
    investor_name = models.CharField(max_length=255)
    edrpou_or_ipn = models.CharField(max_length=20, unique=True, null=True, blank=True)
    investor_description = models.TextField(blank=True)
    investor_phone = models.CharField(max_length=20, blank=True)
    is_verified = models.BooleanField(default=False)
    investor_type = models.CharField(max_length=20, choices=InvestorType.choices)
    investment_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.investor_name