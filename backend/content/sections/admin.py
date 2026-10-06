from django.contrib import admin

from content.admin_mixins import SingletonModelAdmin
from content.sections.models import (
    LandingBanner,
    LandingForWhomCard,
    LandingForWhomSection,
    LandingHero,
    LandingHeroImage,
    LandingWhyWorthItem,
    LandingWhyWorthSection,
)


class LandingHeroImageInline(admin.TabularInline):
    model = LandingHeroImage
    fields = ('title', 'url', 'order')
    extra = 0


class LandingForWhomCardInline(admin.TabularInline):
    model = LandingForWhomCard
    fields = ('title', 'icon', 'description', 'order')
    extra = 0


class LandingWhyWorthItemInline(admin.TabularInline):
    model = LandingWhyWorthItem
    fields = ('title', 'description', 'order')
    extra = 0


@admin.register(LandingHero)
class LandingHeroAdmin(SingletonModelAdmin):
    inlines = (LandingHeroImageInline,)


@admin.register(LandingBanner)
class LandingBannerAdmin(SingletonModelAdmin):
    pass


@admin.register(LandingForWhomSection)
class LandingForWhomSectionAdmin(SingletonModelAdmin):
    inlines = (LandingForWhomCardInline,)


@admin.register(LandingWhyWorthSection)
class LandingWhyWorthSectionAdmin(SingletonModelAdmin):
    inlines = (LandingWhyWorthItemInline,)
