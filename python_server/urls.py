from django.urls import include, path
from dashboard.api import app

urlpatterns = [
    path('', include('dashboard.urls.airtime_urls')),
    path('', include('dashboard.urls.equb_urls')),
    path('', include('dashboard.urls.institution_urls')),
    path('', include('dashboard.urls.invitation_urls')),
    path('', include('dashboard.urls.recurring_contract_urls')),
    path('', include('dashboard.urls.saving_urls')),
    path('', include('dashboard.urls.transaction_urls')),
    path('', include('dashboard.urls.transfer_urls')),
    path('', include('dashboard.urls.user_urls')),
]
