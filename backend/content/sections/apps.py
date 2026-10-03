from django.apps import AppConfig


class SectionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'content.sections'
    label = 'content_sections'
    verbose_name = 'Content: sections'
