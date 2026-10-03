from django.db import models

MAX_LENGTH_INVESTOR_NAME = 255
MAX_LENGTH_EDRPOU_OR_IPN = 20
MAX_LENGTH_INVESTOR_PHONE = 20
MAX_LENGTH_INVESTOR_TYPE = 20
INVESTMENT_MIN_MAX_DIGITS = 12
INVESTMENT_MIN_DECIMAL_PLACES = 2


class InvestorProfile(models.Model):
    class InvestorType(models.TextChoices):
        PRIVATE = 'private', 'Приватна особа'
        FUND = 'fund', 'Фонд'
        COMPANY = 'company', 'Компанія'

    investor_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        'users.User',
        on_delete=models.RESTRICT,
        related_name='investor_profile',
    )
    investor_name = models.CharField(max_length=MAX_LENGTH_INVESTOR_NAME)
    edrpou_or_ipn = models.CharField(
        max_length=MAX_LENGTH_EDRPOU_OR_IPN,
        unique=True,
        null=True,
        blank=True,
    )
    investor_description = models.TextField(blank=True)
    investor_phone = models.CharField(
        max_length=MAX_LENGTH_INVESTOR_PHONE,
        blank=True,
    )
    is_verified = models.BooleanField(default=False)
    investor_type = models.CharField(
        max_length=MAX_LENGTH_INVESTOR_TYPE,
        choices=InvestorType.choices,
    )
    investment_min = models.DecimalField(
        max_digits=INVESTMENT_MIN_MAX_DIGITS,
        decimal_places=INVESTMENT_MIN_DECIMAL_PLACES,
        null=True,
        blank=True,
    )

    class Meta:
        indexes = [
            models.Index(fields=['investor_type'], name='investor_type_idx'),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(investment_min__isnull=True)
                    | models.Q(investment_min__gte=0)
                ),
                name='investor_investment_min_non_negative',
            ),
        ]

    def __str__(self):
        return self.investor_name
