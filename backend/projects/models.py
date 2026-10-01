from django.db import models
from startups.models import StartupProfile 

MAX_LENGTH_PROJECT_TITLE = 255
MAX_LENGTH_INVESTMENT_SUM = 12
MAX_LENGTH_RAISED_AMOUNT = 12
MAX_LENGTH_PROJECT_STAGE = 100

class Project(models.Model):
    project_id = models.AutoField(primary_key=True)
    startup = models.ForeignKey(
        StartupProfile, 
        on_delete=models.RESTRICT, 
        related_name='projects'
    )
    project_title = models.CharField(max_length=MAX_LENGTH_PROJECT_TITLE)
    project_description = models.TextField()
    investment_sum = models.DecimalField(max_digits=MAX_LENGTH_INVESTMENT_SUM, decimal_places=2)
    project_stage = models.CharField(max_length=MAX_LENGTH_PROJECT_STAGE)
    raised_amount = models.DecimalField(max_digits=MAX_LENGTH_RAISED_AMOUNT, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['project_stage'], name='project_stage_idx'),
        ]

    def __str__(self):
        return self.project_title


