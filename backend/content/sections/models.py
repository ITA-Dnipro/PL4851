from django.db import models

MAX_LENGTH_TITLE = 255
MAX_LENGTH_URL = 255
MAX_LENGTH_CTA = 50
MAX_LENGTH_ICON = 50


class LandingHero(models.Model):
    title = models.CharField(max_length=MAX_LENGTH_TITLE)
    subtitle = models.TextField(blank=True)
    cta_text = models.CharField(max_length=MAX_LENGTH_CTA, blank=True)
    cta_url = models.CharField(max_length=MAX_LENGTH_URL, blank=True)

    class Meta:
        verbose_name = 'Landing Hero'
        verbose_name_plural = 'Landing Hero'

    def __str__(self):
        return self.title


class LandingHeroImage(models.Model):
    hero = models.ForeignKey(
        LandingHero, on_delete=models.CASCADE, related_name='images'
    )
    title = models.CharField(max_length=MAX_LENGTH_TITLE)
    url = models.CharField(max_length=MAX_LENGTH_URL)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class LandingBanner(models.Model):
    title = models.CharField(max_length=MAX_LENGTH_TITLE)
    cta_text = models.CharField(max_length=MAX_LENGTH_CTA, blank=True)
    cta_url = models.CharField(max_length=MAX_LENGTH_URL, blank=True)

    class Meta:
        verbose_name = 'Landing Banner'
        verbose_name_plural = 'Landing Banner'

    def __str__(self):
        return self.title


class LandingForWhomSection(models.Model):
    title = models.CharField(max_length=MAX_LENGTH_TITLE)

    class Meta:
        verbose_name = 'Landing For Whom'
        verbose_name_plural = 'Landing For Whom'

    def __str__(self):
        return self.title


class LandingForWhomCard(models.Model):
    section = models.ForeignKey(
        LandingForWhomSection, on_delete=models.CASCADE, related_name='cards'
    )
    title = models.CharField(max_length=MAX_LENGTH_TITLE)
    icon = models.CharField(max_length=MAX_LENGTH_ICON)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class LandingWhyWorthSection(models.Model):
    title = models.CharField(max_length=MAX_LENGTH_TITLE)

    class Meta:
        verbose_name = 'Landing Why Worth'
        verbose_name_plural = 'Landing Why Worth'

    def __str__(self):
        return self.title


class LandingWhyWorthItem(models.Model):
    section = models.ForeignKey(
        LandingWhyWorthSection, on_delete=models.CASCADE, related_name='items'
    )
    title = models.CharField(max_length=MAX_LENGTH_TITLE)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title
