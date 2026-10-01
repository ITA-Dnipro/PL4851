from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "user_id",
        "email",
        "first_name",
        "last_name",
        "role",
        "is_active",
        "created_at",
    )
    list_filter = ("role", "is_active")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    readonly_fields = ("created_at", "last_login")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Персональна інформація",
            {"fields": ("first_name", "last_name", "role")},
        ),
        (
            "Права доступу",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Дати", {"fields": ("created_at", "last_login")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "role",
                ),
            },
        ),
    )