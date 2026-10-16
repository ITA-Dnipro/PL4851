from django.urls import path

from startups.views import StartupProfileListView, StartupPublicProfileDetailView

app_name = 'startups'

urlpatterns = [
    path('', StartupProfileListView.as_view(), name='startup-list'),
    path('<int:id>/', StartupPublicProfileDetailView.as_view(), name='startup-detail'),
]
