from django.contrib import admin

from .models import SavedProject


@admin.register(SavedProject)
class SavedProjectAdmin(admin.ModelAdmin):
    list_display = ('saved_project_id', 'investor', 'project', 'saved_at')
