from django.urls import path

from dashboard.views import SavedItemsListView

urlpatterns = [
    path('users/<int:id>/saved/', SavedItemsListView.as_view(), name='saved-items'),
]
