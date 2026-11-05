# dashboard/views.py
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from dashboard.models import SavedProject
from dashboard.permissions import IsOwnerOrAdmin
from dashboard.serializers import SavedProjectSerializer

DEFAULT_PAGE_SIZE = 12
MAX_PAGE_SIZE = 50
PAGE_SIZE_QUERY_PARAM = 'page_size'
TYPE = 'project'


class SavedItemsPagination(PageNumberPagination):
    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = PAGE_SIZE_QUERY_PARAM
    max_page_size = MAX_PAGE_SIZE


class SavedItemsListView(ListAPIView):
    serializer_class = SavedProjectSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    pagination_class = SavedItemsPagination

    def get_queryset(self):
        item_type = self.request.query_params.get('type')
        if item_type and item_type != TYPE:
            raise ValidationError({'type': f'Unsupported type: {item_type}.'})

        return (
            SavedProject.objects.filter(investor__user_id=self.kwargs['id'])
            .select_related('project__startup')
            .prefetch_related('project__startup__industries')
            .order_by('-saved_at')
        )
