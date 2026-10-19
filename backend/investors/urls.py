from django.urls import path

from investors.views import InvestorProfileDetailView, InvestorProfileListView

app_name = 'investors'

urlpatterns = [
    path('', InvestorProfileListView.as_view(), name='investor-list'),
    path('<int:id>/', InvestorProfileDetailView.as_view(), name='investor-detail'),
]
