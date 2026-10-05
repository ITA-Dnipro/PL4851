from django.urls import path

from startups.views import StartupProfileListView

app_name = 'startups'

urlpatterns = [
    path('', StartupProfileListView.as_view(), name='startup-list'),
]
