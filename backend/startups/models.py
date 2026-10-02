import re
from django.db import models
from users.models import User


MAX_LENGTH_STARTUP_NAME = 255
MAX_LENGTH_EDRPOU_OR_IPN = 20
MAX_LENGTH_WEBSITE = 200
MAX_LENGTH_STARTUP_PHONE = 20
MAX_LENGTH_INDUSTRY = 100
DEFAULT_EMPLOYEES = 1
NON_DIGIT_PATTERN = re.compile(r"\D")


class StartupProfile(models.Model):
    startup_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        User,
        on_delete=models.RESTRICT,
        to_field="user_id",
        related_name="startup_profile",
    )
    startup_name = models.CharField(max_length=MAX_LENGTH_STARTUP_NAME)
    edrpou_or_ipn = models.CharField(
        max_length=MAX_LENGTH_EDRPOU_OR_IPN,
        unique=True,
        blank=True,
        null=True,
    )
    startup_description = models.TextField()
    website = models.URLField(max_length=MAX_LENGTH_WEBSITE, blank=True)
    startup_phone = models.CharField(max_length=MAX_LENGTH_STARTUP_PHONE)
    address = models.TextField(blank=True)
    industry = models.CharField(max_length=MAX_LENGTH_INDUSTRY)
    founded_at = models.DateField(blank=True, null=True)
    employees = models.IntegerField(default=DEFAULT_EMPLOYEES)
    is_verified = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["industry"], name="startup_industry_idx"),
        ]

    def save(self, *args, **kwargs):
        if self.startup_phone:
            self.startup_phone = NON_DIGIT_PATTERN.sub("", self.startup_phone)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.startup_name