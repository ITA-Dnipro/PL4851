from django.urls import path

from users.views.login import LoginView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
]
