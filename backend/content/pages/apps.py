from django.apps import AppConfig


class PagesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'content.pages'
    label = 'content_pages'
    verbose_name = 'Content: pages'
