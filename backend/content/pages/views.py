from django.http import Http404
from rest_framework.response import Response
from rest_framework.views import APIView

from content.pages.models import LandingPage
from content.sections.models import (
    LandingBanner,
    LandingForWhomSection,
    LandingHero,
    LandingWhyWorthSection,
)
from content.sections.serializers import (
    LandingBannerSerializer,
    LandingForWhomSectionSerializer,
    LandingHeroSerializer,
    LandingWhyWorthSectionSerializer,
)


def serialize_block(is_shown, queryset, serializer_class):
    """Serialize a singleton block, or return None if it is hidden or missing."""
    if not is_shown:
        return None

    block = queryset.first()
    return serializer_class(block).data if block is not None else None


class LandingContentView(APIView):
    def get(self, request):
        page = LandingPage.objects.first()
        if page is None:
            raise Http404('Landing page is not configured')

        return Response(
            {
                'hero': serialize_block(
                    page.show_hero,
                    LandingHero.objects.prefetch_related('images'),
                    LandingHeroSerializer,
                ),
                'banner': serialize_block(
                    page.show_banner,
                    LandingBanner.objects.all(),
                    LandingBannerSerializer,
                ),
                'for_whom': serialize_block(
                    page.show_for_whom,
                    LandingForWhomSection.objects.prefetch_related('cards'),
                    LandingForWhomSectionSerializer,
                ),
                'why_worth': serialize_block(
                    page.show_why_worth,
                    LandingWhyWorthSection.objects.prefetch_related('items'),
                    LandingWhyWorthSectionSerializer,
                ),
            }
        )
