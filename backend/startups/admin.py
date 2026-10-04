from django.contrib import admin
from .models import StartupProfile

@admin.register(StartupProfile)
class StartupProfileAdmin(admin.ModelAdmin):
    list_display = (
        'startup_id',
        'startup_name', 
        'edrpou_or_ipn', 
        'startup_description',
        'website',
        'startup_phone',
        'address', 
        'founded_at',
        'employees',
        'is_verified' 
    )
    filter_horizontal = ('industries',)
