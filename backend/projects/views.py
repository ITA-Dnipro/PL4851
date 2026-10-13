from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.pagination import PageNumberPagination

from startups.models import StartupProfile

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
        startup = get_object_or_404(StartupProfile, pk=startup_id)
        queryset = (
            Project.objects.filter(startup=startup)
            .exclude(status=Project.ProjectStatus.DRAFT)
            .order_by('-created_at')
        )
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)

        return queryset
