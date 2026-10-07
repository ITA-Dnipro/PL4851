import re

from django.db import models

from users.models import User

MAX_LENGTH_STARTUP_NAME = 255
MAX_LENGTH_EDRPOU_OR_IPN = 20
MAX_LENGTH_WEBSITE = 200
MAX_LENGTH_STARTUP_PHONE = 20
MAX_LENGTH_INDUSTRY = 100
MAX_LENGTH_LOCATION = 50
MAX_LENGTH_LOGO = 255
DEFAULT_EMPLOYEES = 1
NON_DIGIT_PATTERN = re.compile(r'\D')


class Industry(models.Model):
    class IndustryType(models.TextChoices):
        IT = 'it', 'Інформаційні технології / IT'
        FINANCE = 'finance', 'Фінанси та FinTech'
        HEALTHCARE = 'healthcare', "Медицина та охорона здоров'я"
        EDUCATION = 'education', 'Освіта'
        AGRICULTURE = 'agriculture', 'Сільське господарство'
        E_COMMERCE = 'e_commerce', 'Електронна торгівля'
        GREEN_ENERGY = 'green_energy', 'Зелена енергетика / Екологія'
        FOOD = 'food', 'Їжа / Харчова промисловість'
        BEVERAGES = 'beverages', 'Напої'
        PACKAGING = 'packaging', 'Пакування та тара'
        CATERING = 'catering', 'Кейтеринг'
        WINEMAKING = 'winemaking', 'Виноробство'
        CRAFT = 'craft', 'Ремесла'
        TOURISM = 'tourism', 'Туризм'
        OTHER = 'other', 'Інше'

    industry_id = models.AutoField(primary_key=True)
    slug = models.SlugField(max_length=MAX_LENGTH_INDUSTRY, unique=True)
    industry_name = models.CharField(max_length=MAX_LENGTH_INDUSTRY, unique=True)

    class Meta:
        ordering = ['industry_name']

    def __str__(self):
        return self.industry_name


class LocationType(models.TextChoices):
    CHERNIVTSI = 'chernivtsi', 'Чернівецька область'
    CHERKASY = 'cherkasy', 'Черкаська область'
    CHERNIHIV = 'chernihiv', 'Чернігівська область'
    DNIPRO = 'dnipro', 'Дніпропетровська область'
    DONETSK = 'donetsk', 'Донецька область'
    IVANO_FRANKIVSK = 'ivano_frankivsk', 'Івано-Франківська область'
    KHARKIV = 'kharkiv', 'Харківська область'
    KHERSON = 'kherson', 'Херсонська область'
    KHMELNYTSKYI = 'khmelnytskyi', 'Хмельницька область'
    KYIV_CITY = 'kyiv_city', 'м. Київ'
    KYIV = 'kyiv', 'Київська область'
    KIROVOHRAD = 'kirovohrad', 'Кіровоградська область'
    LUHANSK = 'luhansk', 'Луганська область'
    LVIV = 'lviv', 'Львівська область'
    MYKOLAIV = 'mykolaiv', 'Миколаївська область'
    ODESA = 'odesa', 'Одеська область'
    POLTAVA = 'poltava', 'Полтавська область'
    RIVNE = 'rivne', 'Рівненська область'
    SUMY = 'sumy', 'Сумська область'
    TERNOPIL = 'ternopil', 'Тернопільська область'
    VINNYTSIA = 'vinnytsia', 'Вінницька область'
    VOLYN = 'volyn', 'Волинська область'
    ZAKARPATTIA = 'zakarpattia', 'Закарпатська область'
    ZAPORIZHZHIA = 'zaporizhzhia', 'Запорізька область'
    ZHYTOMYR = 'zhytomyr', 'Житомирська область'
    CRIMEA = 'crimea', 'Автономна Республіка Крим'


class StartupProfile(models.Model):
    startup_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        User,
        on_delete=models.RESTRICT,
        to_field='user_id',
        related_name='startup_profile',
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
    location = models.CharField(
        max_length=MAX_LENGTH_LOCATION,
        choices=LocationType.choices,
        default=LocationType.KYIV_CITY,
    )
    industries = models.ManyToManyField(Industry, related_name='startup_profiles')
    founded_at = models.DateField(blank=True, null=True)
    logo = models.ImageField(
        upload_to='thumbs/', blank=True, null=True, max_length=MAX_LENGTH_LOGO
    )
    employees = models.IntegerField(default=DEFAULT_EMPLOYEES)
    is_verified = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['location'], name='startup_location_idx'),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(employees__gte=1),
                name='startup_employees_gte_one',
            ),
        ]

    def save(self, *args, **kwargs):
        if self.startup_phone:
            self.startup_phone = NON_DIGIT_PATTERN.sub('', self.startup_phone)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.startup_name
