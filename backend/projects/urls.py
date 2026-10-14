from django.urls import path

from .views import StartupProjectListView

app_name = 'projects'

urlpatterns = [
    path(
        'startups/<int:startup_id>/projects/',
        StartupProjectListView.as_view(),
        name='startup-projects-list',
    ),
]
