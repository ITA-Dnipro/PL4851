from django.db.models import Count, Q
from rest_framework import filters, generics, permissions
from rest_framework.pagination import PageNumberPagination

from startups.models import StartupProfile
from startups.serializers import (
    StartupProfileSerializer,
    StartupPublicProfileSerializer,
)


class StartupPagination(PageNumberPagination):
    """Custom pagination class to match the API specification."""

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
        base_queryset = StartupProfile.objects.filter(is_verified=True)
        tag = self.request.query_params.get('tag')
        if tag:
            base_queryset = base_queryset.filter(industries__slug=tag)

        optimized_queryset = (
            base_queryset.only(
                'startup_id', 'startup_name', 'short_description', 'logo', 'location'
            )
            .prefetch_related('industries')
            .order_by('startup_id')
        )

        return optimized_queryset


class StartupPublicProfileDetailView(generics.RetrieveAPIView):
    """Returns the full public data of a single startup"""

    serializer_class = StartupPublicProfileSerializer
    lookup_field = 'startup_id'
    lookup_url_kwarg = 'id'
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        optimized_queryset = (
            StartupProfile.objects.filter(is_verified=True)
            .annotate(
                _followers_count=Count('followers', distinct=True),
                _projects_count=Count(
                    'projects', filter=~Q(projects__status='draft'), distinct=True
                ),
            )
            .prefetch_related('industries')
        )

        return optimized_queryset
