from django.urls import path

from content.pages.views import LandingContentView

urlpatterns = [
    path('landing/', LandingContentView.as_view(), name='landing-content'),
]
