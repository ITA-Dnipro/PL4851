from django.db import models
from investors.models import InvestorProfile
from projects.models import Project

class SavedProject(models.Model):
    saved_project_id = models.AutoField(primary_key=True)
    investor = models.ForeignKey(
        InvestorProfile, 
        on_delete=models.RESTRICT, 
        related_name='saved_projects'
    )
    project = models.ForeignKey(
        Project, 
        on_delete=models.RESTRICT, 
        related_name='saved_by_investors'
    )
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('investor', 'project')

    def __str__(self):
        return f"{self.investor.investor_name} -> {self.project.project_title}"
