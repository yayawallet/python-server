from django.urls import include, path
from django.contrib import admin

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
    path('', include('dashboard.urls.scheduled_urls')),
    path('', include('dashboard.urls.report_urls')),
    path('', include('dashboard.urls.bill_urls')),
    path('', include('dashboard.urls.auth_urls')),
    path('admin', admin.site.urls),
]
