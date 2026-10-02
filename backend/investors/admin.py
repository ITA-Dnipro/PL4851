from django.contrib import admin
from .models import InvestorProfile


@admin.register(InvestorProfile)
class InvestorProfileAdmin(admin.ModelAdmin):
    list_display = (
        "investor_id",
        "investor_name",
        "user",
        "edrpou_or_ipn",
        "investor_phone",
        "investor_type",
        "investment_min",
        "is_verified",
    )
    list_filter = ("is_verified", "investor_type")
    search_fields = ("investor_name", "edrpou_or_ipn", "user__email")
    list_select_related = ("user",)
    ordering = ("investor_name",)
