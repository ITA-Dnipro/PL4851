from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import PasswordResetMetrics, PasswordResetToken, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'user_id',
        'email',
        'first_name',
        'last_name',
        'role',
        'is_active',
        'created_at',
    )
    list_filter = ('role', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    readonly_fields = ('created_at', 'last_login')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            'Персональна інформація',
            {'fields': ('first_name', 'last_name', 'role')},
        ),
        (
            'Права доступу',
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                )
            },
        ),
        ('Дати', {'fields': ('created_at', 'last_login')}),
    )

    add_fieldsets = (
        (
            None,
            {
                'fields': (
                    'email',
                    'password1',
                    'password2',
                    'first_name',
                    'last_name',
                    'role',
                ),
            },
        ),
    )


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'token_hash',
        'created_at',
        'expires_at',
        'used_at',
        'revoked',
    )
    list_filter = ('revoked', 'used_at', 'created_at', 'expires_at')
    search_fields = ('user__email', 'token_hash')
    actions = ('revoke_tokens',)

    @admin.action(description='Revoke selected tokens')
    def revoke_tokens(self, request, queryset):
        queryset.update(revoked=True)


@admin.register(PasswordResetMetrics)
class PasswordResetMetricsAdmin(admin.ModelAdmin):
    list_display = (
        'requests',
        'confirms',
        'expired_attempts',
        'reused_attempts',
    )
    readonly_fields = (
        'requests',
        'confirms',
        'expired_attempts',
        'reused_attempts',
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
