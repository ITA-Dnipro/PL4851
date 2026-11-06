from django.conf import settings
from django.db import models, router

from shared.slug_utils import save_with_unique_slug

MAX_LENGTH_PROJECT_TITLE = 255
MAX_LENGTH_PROJECT_STAGE = 100
MAX_LENGTH_STATUS = 20
MAX_LENGTH_VISIBILITY = 8
MAX_LENGTH_SHORT_DESCRIPTION = 255
MAX_LENGTH_LOGO = 255
MAX_LENGTH_SLUG = 255
MAX_LENGTH_CURRENCY = 3
INVESTMENT_SUM_MAX_DIGITS = 12
INVESTMENT_SUM_DECIMAL_PLACES = 2
RAISED_AMOUNT_MAX_DIGITS = 12
RAISED_AMOUNT_DECIMAL_PLACES = 2


class Project(models.Model):
    class ProjectStatus(models.TextChoices):
        DRAFT = 'draft', 'Чернетка'
        ACTIVE = 'active', 'Активний'
        PAUSED = 'paused', 'Призупинений'
        CLOSED = 'closed', 'Закритий'

    class Visibility(models.TextChoices):
        PUBLIC = 'public', 'Публічний'
        PRIVATE = 'private', 'Приватний'
        UNLISTED = 'unlisted', 'За посиланням'

    project_id = models.AutoField(primary_key=True)
    startup = models.ForeignKey(
        'startups.StartupProfile',
        on_delete=models.RESTRICT,
        related_name='projects',
    )
    project_title = models.CharField(max_length=MAX_LENGTH_PROJECT_TITLE)
    short_description = models.CharField(
        max_length=MAX_LENGTH_SHORT_DESCRIPTION, blank=True, default=''
    )
    project_description = models.TextField()
    investment_sum = models.DecimalField(
        max_digits=INVESTMENT_SUM_MAX_DIGITS,
        decimal_places=INVESTMENT_SUM_DECIMAL_PLACES,
    )
    project_stage = models.CharField(
        max_length=MAX_LENGTH_PROJECT_STAGE, default='idea'
    )
    raised_amount = models.DecimalField(
        max_digits=RAISED_AMOUNT_MAX_DIGITS,
        decimal_places=RAISED_AMOUNT_DECIMAL_PLACES,
        default=0,
    )
    slug = models.SlugField(max_length=MAX_LENGTH_SLUG, unique=True, blank=True)
    currency = models.CharField(max_length=MAX_LENGTH_CURRENCY, default='UAH')
    industries = models.ManyToManyField(
        'startups.Industry',
        related_name='projects',
        blank=True,
    )
    visibility = models.CharField(
        max_length=MAX_LENGTH_VISIBILITY,
        choices=Visibility.choices,
        default=Visibility.PUBLIC,
    )
    status = models.CharField(
        max_length=MAX_LENGTH_STATUS,
        choices=ProjectStatus.choices,
        default=ProjectStatus.DRAFT,
    )
    logo = models.ImageField(
        upload_to='projects/logos/%Y/%m/',
        blank=True,
        null=True,
        max_length=MAX_LENGTH_LOGO,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['project_stage'], name='project_stage_idx'),
            models.Index(fields=['status'], name='project_status_idx'),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(investment_sum__gt=0),
                name='project_investment_sum_gt_zero',
            ),
            models.CheckConstraint(
                condition=models.Q(raised_amount__gte=0),
                name='project_raised_amount_gte_zero',
            ),
        ]

    def __str__(self):
        return self.project_title

    def save(self, *args, **kwargs):
        using = kwargs.get('using') or router.db_for_write(type(self), instance=self)
        kwargs['using'] = using

        def save_instance():
            super(Project, self).save(*args, **kwargs)

        save_with_unique_slug(
            self,
            save_instance,
            self.project_title,
            Project.objects.using(using),
            MAX_LENGTH_SLUG,
            'project',
        )


class ProjectAttachment(models.Model):
    class AttachmentType(models.TextChoices):
        IMAGE = 'image', 'Зображення'
        PDF = 'pdf', 'PDF'

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='attachments',
    )
    type = models.CharField(max_length=5, choices=AttachmentType.choices)
    order = models.PositiveIntegerField(default=0)
    caption = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        ordering = ['order', 'pk']

    def __str__(self):
        return f'{self.get_type_display()} — {self.project}'


class ProjectAudit(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='audit_events',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='project_audit_events',
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    changes = models.JSONField(default=dict)

    class Meta:
        ordering = ['-timestamp', '-pk']
