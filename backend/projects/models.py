from django.db import models

MAX_LENGTH_PROJECT_TITLE = 255
MAX_LENGTH_PROJECT_STAGE = 100
INVESTMENT_SUM_MAX_DIGITS = 12
INVESTMENT_SUM_DECIMAL_PLACES = 2
RAISED_AMOUNT_MAX_DIGITS = 12
RAISED_AMOUNT_DECIMAL_PLACES = 2


class Project(models.Model):
    project_id = models.AutoField(primary_key=True)
    startup = models.ForeignKey(
        'startups.StartupProfile',
        on_delete=models.RESTRICT,
        related_name='projects',
    )
    project_title = models.CharField(max_length=MAX_LENGTH_PROJECT_TITLE)
    project_description = models.TextField()
    investment_sum = models.DecimalField(
        max_digits=INVESTMENT_SUM_MAX_DIGITS,
        decimal_places=INVESTMENT_SUM_DECIMAL_PLACES,
    )
    project_stage = models.CharField(max_length=MAX_LENGTH_PROJECT_STAGE)
    raised_amount = models.DecimalField(
        max_digits=RAISED_AMOUNT_MAX_DIGITS,
        decimal_places=RAISED_AMOUNT_DECIMAL_PLACES,
        default=0,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['project_stage'], name='project_stage_idx'),
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
