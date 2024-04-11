from django.urls import include, path
from dashboard.api import app

urlpatterns = [
    path('api/', include('dashboard.urls.airtime_urls')),
    path('api/', include('dashboard.urls.equb_urls')),
    path('api/', include('dashboard.urls.institution_urls')),
    path('api/', include('dashboard.urls.invitation_urls')),
    path('api/', include('dashboard.urls.recurring_contract_urls')),
    path('api/', include('dashboard.urls.saving_urls')),
    path('api/', include('dashboard.urls.transaction_urls')),
    path('api/', include('dashboard.urls.transfer_urls')),
    path('api/', include('dashboard.urls.user_urls')),
]
