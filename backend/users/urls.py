from django.urls import path

from users.views.login import LoginView
from users.views.logout import LogoutView
from users.views.password_reset_confirm import PasswordResetConfirmView
from users.views.password_reset_request import PasswordResetRequestView
from users.views.refresh import RefreshView
from users.views.register import RegisterView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/', RefreshView.as_view(), name='refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path(
        'password-reset/confirm/',
        PasswordResetConfirmView.as_view(),
        name='password-reset-confirm',
    ),
    path(
        'password-reset/',
        PasswordResetRequestView.as_view(),
        name='password-reset',
    ),
]
