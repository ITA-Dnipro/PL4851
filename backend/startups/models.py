import re
from django.db import models
from users.models import User

MAX_LENGTH_STARTUP_NAME = 255
MAX_LENGTH_EDRPOU_OR_IPN = 20
MAX_LENGTH_WEBSITE = 200
MAX_LENGTH_STARTUP_PHONE = 20
MAX_LENGTH_INDUSTRY = 100
MAX_LENGTH_ADDRESS = 255

class StartupProfile(models.Model):
    class IndustryType(models.TextChoices):
        IT = "it", "Інформаційні технології / IT"
        FINANCE = "finance", "Фінанси та FinTech"
        HEALTHCARE = "healthcare", "Медицина та охорона здоров'я"
        EDUCATION = "education", "Освіта"
        AGRICULTURE = "agriculture", "Сільське господарство"
        E_COMMERCE = "e_commerce", "Електронна торгівля"
        GREEN_ENERGY = "green_energy", "Зелена енергетика / Екологія"
        FOOD = "food", "Їжа / Харчова промисловість"
        BEVERAGES = "beverages", "Напої"
        PACKAGING = "packaging", "Пакування та тара"
        CATERING = "catering", "Кейтеринг / Ресторанний бізнес"
        WINEMAKING = "winemaking", "Виноробство"
        OTHER = "other", "Інше"

    startup_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        User, 
        on_delete=models.RESTRICT, 
        to_field='user_id',
        related_name='startup_profile'
    )
    startup_name = models.CharField(max_length=MAX_LENGTH_STARTUP_NAME)
    edrpou_or_ipn = models.CharField(max_length=MAX_LENGTH_EDRPOU_OR_IPN, unique=True, blank=True, null=True)
    startup_description = models.TextField()
    website = models.URLField(max_length=MAX_LENGTH_WEBSITE, blank=True)
    startup_phone = models.CharField(max_length=MAX_LENGTH_STARTUP_PHONE)
    address = models.TextField(blank=True)
    industry = models.CharField(
        max_length=MAX_LENGTH_INDUSTRY,
        choices=IndustryType.choices,
        default=IndustryType.OTHER
    )
    founded_at = models.DateField(blank=True, null=True)
    employees = models.IntegerField(default=1)
    is_verified = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['industry'], name='startup_industry_idx'),
        ]

    def save(self, *args, **kwargs):
        if self.startup_phone:
            self.startup_phone = re.sub(r'\D', '', self.startup_phone)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.startup_name
