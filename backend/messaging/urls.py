from django.urls import path

from messaging.views import (
    ConversationListCreateView,
    ConversationReadView,
    MessageListCreateView,
)

app_name = 'messaging'

urlpatterns = [
    path('', ConversationListCreateView.as_view(), name='conversation-list'),
    path(
        '<str:conversation_id>/messages/',
        MessageListCreateView.as_view(),
        name='message-list',
    ),
    path(
        '<str:conversation_id>/read/',
        ConversationReadView.as_view(),
        name='conversation-read',
    ),
]
