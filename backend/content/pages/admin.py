from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from content.admin_mixins import SingletonModelAdmin
from content.pages.models import LandingPage
from content.sections.models import (
    LandingBanner,
    LandingForWhomSection,
    LandingHero,
    LandingWhyWorthSection,
)

# Visibility flag -> block it controls, in the order of the blocks on the page
LANDING_BLOCKS = {
    'show_hero': LandingHero,
    'show_banner': LandingBanner,
    'show_for_whom': LandingForWhomSection,
    'show_why_worth': LandingWhyWorthSection,
}


def block_link(model):
    """Link to the edit form of a singleton block (or to its add form)."""
    opts = model._meta
    block = model.objects.first()
    if block is None:
        url = reverse(f'admin:{opts.app_label}_{opts.model_name}_add')
        return format_html('<a href="{}">Create</a>', url)

    url = reverse(f'admin:{opts.app_label}_{opts.model_name}_change', args=[block.pk])
    return format_html('<a href="{}">Edit</a>', url)


@admin.register(LandingPage)
class LandingPageAdmin(SingletonModelAdmin):
    fieldsets = (('Blocks shown on the page', {'fields': tuple(LANDING_BLOCKS)}),)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for field_name, model in LANDING_BLOCKS.items():
            form.base_fields[field_name].help_text = block_link(model)
        return form
