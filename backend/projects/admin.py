from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'project_id',
        'project_title',
        'project_description',
        'investment_sum',
        'project_stage',
        'raised_amount',
        'created_at',
        'updated_at',
    )
