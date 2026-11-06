from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListCreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from dashboard.models import SavedProject
from dashboard.permissions import IsOwnerOrAdmin
from dashboard.serializers import SavedProjectSerializer, SaveItemSerializer
from investors.models import InvestorProfile
from projects.models import Project

DEFAULT_PAGE_SIZE = 12
MAX_PAGE_SIZE = 50
PAGE_SIZE_QUERY_PARAM = 'page_size'
TYPE = 'project'


class SavedItemsPagination(PageNumberPagination):
    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = PAGE_SIZE_QUERY_PARAM
    max_page_size = MAX_PAGE_SIZE


class SavedItemsListView(ListCreateAPIView):
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

    def create(self, request, *args, **kwargs):
        serializer = SaveItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        investor = get_object_or_404(InvestorProfile, user_id=self.kwargs['id'])
        project = get_object_or_404(Project, pk=serializer.validated_data['target_id'])
        saved, created = SavedProject.objects.get_or_create(
            investor=investor, project=project
        )
        return Response(
            {'saved_id': saved.saved_project_id, 'saved_at': saved.saved_at},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class SavedItemDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def delete(self, request, id, saved_id):
        saved = get_object_or_404(SavedProject, pk=saved_id, investor__user_id=id)
        saved.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
