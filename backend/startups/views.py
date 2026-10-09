from rest_framework import filters, generics
from rest_framework.pagination import PageNumberPagination

from startups.models import StartupProfile
from startups.serializers import StartupProfileSerializer


class StartupPagination(PageNumberPagination):
    """Custom pagination class to match the API specification."""

    default_limit = 8
    page_size = 8
    page_size_query_param = 'page_size'


class StartupProfileListView(generics.ListAPIView):
    """API view to list all startup profiles with filtering and pagination."""

    serializer_class = StartupProfileSerializer
    pagination_class = StartupPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['startup_name']

    def get_queryset(self):
        """Optionally restricts the returned startups by tag."""
        queryset = StartupProfile.objects.prefetch_related('industries').order_by(
            'startup_id'
        )
        tag = self.request.query_params.get('tag')
        if tag:
            queryset = queryset.filter(industries__slug=tag)

        return queryset
