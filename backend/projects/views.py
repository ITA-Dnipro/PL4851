from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination

from .models import Project
from .serializers import ProjectSerializer


class ProjectPagination(PageNumberPagination):
    """Custom pagination class for Project list view."""

    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 100


class StartupProjectListView(ListAPIView):
    """API view to list projects for a specific startup, with status filtering."""

    serializer_class = ProjectSerializer
    pagination_class = ProjectPagination

    def get_queryset(self):
        startup_id = self.kwargs.get('startup_id')
        queryset = Project.objects.filter(startup_id=startup_id)
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)

        return queryset
