from django.db import models


class LandingPage(models.Model):
    show_hero = models.BooleanField('Landing Hero', default=True)
    show_banner = models.BooleanField('Landing Banner', default=True)
    show_for_whom = models.BooleanField('Landing For Whom', default=True)
    show_why_worth = models.BooleanField('Landing Why Worth', default=True)

    class Meta:
        verbose_name = 'Landing Page'
        verbose_name_plural = 'Landing Page'

    def __str__(self):
        return 'Landing Page'
