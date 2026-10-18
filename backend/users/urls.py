from django.urls import path

from users.views.login import LoginView
from users.views.logout import LogoutView
from users.views.refresh import RefreshView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/', RefreshView.as_view(), name='refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
