import re

from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.utils.text import slugify

from users.models import User

UKRAINIAN_TRANSLIT = {
    'а': 'a',
    'б': 'b',
    'в': 'v',
    'г': 'h',
    'ґ': 'g',
    'д': 'd',
    'е': 'e',
    'є': 'ye',
    'ж': 'zh',
    'з': 'z',
    'и': 'y',
    'і': 'i',
    'ї': 'yi',
    'й': 'y',
    'к': 'k',
    'л': 'l',
    'м': 'm',
    'н': 'n',
    'о': 'o',
    'п': 'p',
    'р': 'r',
    'с': 's',
    'т': 't',
    'у': 'u',
    'ф': 'f',
    'х': 'kh',
    'ц': 'ts',
    'ч': 'ch',
    'ш': 'sh',
    'щ': 'shch',
    'ь': '',
    'ю': 'yu',
    'я': 'ya',
}


def custom_slugify(text):
    """Transliterates Ukrainian characters to Latin and then slugifies the result."""
    if not text:
        return ''

    text = text.lower()
    translit_text = ''.join(UKRAINIAN_TRANSLIT.get(char, char) for char in text)

    return slugify(translit_text)


MAX_LENGTH_STARTUP_NAME = 255
MAX_LENGTH_EDRPOU_OR_IPN = 20
MAX_LENGTH_WEBSITE = 200
MAX_LENGTH_STARTUP_PHONE = 20
MAX_LENGTH_SHORT_DESCRIPTION = 255
MAX_LENGTH_INDUSTRY = 100
MAX_LENGTH_LOCATION = 50
MAX_LENGTH_LOGO = 255
DEFAULT_EMPLOYEES = 1
NON_DIGIT_PATTERN = re.compile(r'\D')
MAX_LENGTH_SLUG = 255
MAX_LENGTH_EMAIL = 254


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
    short_description = models.CharField(
        max_length=MAX_LENGTH_SHORT_DESCRIPTION, blank=True, default=''
    )
    startup_description = models.TextField(blank=True, default='')
    website = models.URLField(max_length=MAX_LENGTH_WEBSITE, blank=True)
    startup_phone = models.CharField(
        max_length=MAX_LENGTH_STARTUP_PHONE, blank=True, default=''
    )
    location = models.CharField(
        max_length=MAX_LENGTH_LOCATION,
        choices=LocationType.choices,
        default=LocationType.KYIV_CITY,
    )
    industries = models.ManyToManyField(
        Industry, related_name='startup_profiles', blank=True
    )
    founded_at = models.DateField(blank=True, null=True)
    logo = models.ImageField(
        upload_to='startups/logos/%Y/%m/',
        blank=True,
        null=True,
        max_length=MAX_LENGTH_LOGO,
    )
    employees = models.IntegerField(default=DEFAULT_EMPLOYEES)
    is_verified = models.BooleanField(default=False)
    slug = models.SlugField(max_length=MAX_LENGTH_SLUG, unique=True)
    hero_image = models.ImageField(
        upload_to='startups/hero_images/%Y/%m/', blank=True, null=True
    )
    startup_email = models.EmailField(
        max_length=MAX_LENGTH_EMAIL, blank=True, default=''
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['location'], name='startup_location_idx'),
            models.Index(fields=['created_at'], name='startup_created_at_idx'),
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

        if self.startup_email:
            clean_email = self.startup_email.strip()
            self.startup_email = BaseUserManager.normalize_email(clean_email)

        if not self.slug:
            base_slug = custom_slugify(self.startup_name)
            if not base_slug:
                base_slug = 'startup'
            base_slug = base_slug[:MAX_LENGTH_SLUG].rstrip('-')
            unique_slug = base_slug
            counter = 1

            queryset = StartupProfile.objects.filter(slug=unique_slug)
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)

            while queryset.exists():
                suffix = f'-{counter}'
                allowed_base_len = MAX_LENGTH_SLUG - len(suffix)
                unique_slug = f"{base_slug[:allowed_base_len].rstrip('-')}{suffix}"
                counter += 1

                queryset = StartupProfile.objects.filter(slug=unique_slug)
                if self.pk:
                    queryset = queryset.exclude(pk=self.pk)

            self.slug = unique_slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.startup_name


class StartupFollower(models.Model):
    follower_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        to_field='user_id',
        related_name='following_startups',
    )
    startup = models.ForeignKey(
        StartupProfile,
        on_delete=models.RESTRICT,
        to_field='startup_id',
        related_name='followers',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['created_at'], name='follower_created_at_idx'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'startup'], name='unique_user_startup_follower'
            ),
        ]
