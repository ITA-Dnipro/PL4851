from django.urls import path

from startups.views import StartupProfileListView, StartupPublicProfileDetailView

app_name = 'startups'

urlpatterns = [
    path('', StartupProfileListView.as_view(), name='startup-list'),
    path('<int:id>/', StartupPublicProfileDetailView.as_view(), name='startup-detail'),
    # Below the id route, so /api/startups/11/ is still looked up by id
    path(
        '<slug:slug>/',
        StartupPublicProfileDetailView.as_view(
            lookup_field='slug', lookup_url_kwarg='slug'
        ),
        name='startup-detail-by-slug',
    ),
]
