from django.urls import include, path
from example.api import app

urlpatterns = [
    path('api/', include('example.urls.airtime_urls')),
    path('api/', include('example.urls.equb_urls')),
    path('api/', include('example.urls.institution_urls')),
    path('api/', include('example.urls.invitation_urls')),
    path('api/', include('example.urls.recurring_contract_urls')),
    path('api/', include('example.urls.saving_urls')),
    path('api/', include('example.urls.transaction_urls')),
    path('api/', include('example.urls.transfer_urls')),
    path('api/', include('example.urls.user_urls')),
]
