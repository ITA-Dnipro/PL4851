from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse


class SingletonModelAdmin(admin.ModelAdmin):
    """Admin for a model that must have exactly one record.

    Adding is allowed only while the record is missing, deleting is disabled,
    and the list page redirects straight to the record's edit form.
    """

    def has_add_permission(self, request):
        return not self.model.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = self.model.objects.first()
        if obj is None:
            return super().changelist_view(request, extra_context)

        opts = self.model._meta
        return redirect(
            reverse(f'admin:{opts.app_label}_{opts.model_name}_change', args=[obj.pk])
        )
