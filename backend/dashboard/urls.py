from django.urls import path

from dashboard.views import SavedItemDeleteView, SavedItemsListView

urlpatterns = [
    path('users/<int:id>/saved/', SavedItemsListView.as_view(), name='saved-items'),
    path('users/<int:id>/saved/', SavedItemsListView.as_view(), name='saved-items'),
    path(
        'users/<int:id>/saved/<int:saved_id>/',
        SavedItemDeleteView.as_view(),
        name='saved-item-delete',
    ),
]
