from django.urls import path

from notifications.views import NotificationListView, NotificationMarkReadView

app_name = 'notifications'

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path(
        '<int:notification_id>/read/',
        NotificationMarkReadView.as_view(),
        name='notification-read',
    ),
]
