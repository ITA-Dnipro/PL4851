from rest_framework import filters, generics, permissions
from rest_framework.pagination import PageNumberPagination

from investors.models import InvestorProfile
from investors.serializers import (
    InvestorProfileDetailSerializer,
    InvestorProfileListSerializer,
)


class InvestorPagination(PageNumberPagination):
    """Page number pagination with an adjustable page size."""

    page_size = 8
    page_size_query_param = 'page_size'
    max_page_size = 100


class InvestorProfileListView(generics.ListAPIView):
    """Lists verified investors with search, type filter and pagination."""

    serializer_class = InvestorProfileListSerializer
    pagination_class = InvestorPagination
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['investor_name']

    def get_queryset(self):
        """Optionally restricts the returned investors by type (?type=fund)."""
        queryset = InvestorProfile.objects.filter(is_verified=True).order_by(
            'investor_id'
        )
        investor_type = self.request.query_params.get('type')
        if investor_type:
            queryset = queryset.filter(investor_type=investor_type)

        return queryset


class InvestorProfileDetailView(generics.RetrieveAPIView):
    """Returns the full public data of a single verified investor."""

    serializer_class = InvestorProfileDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'investor_id'
    lookup_url_kwarg = 'id'

    def get_queryset(self):
        # Unverified investors aren't public: they get 404 like unknown ids
        return InvestorProfile.objects.filter(is_verified=True)
