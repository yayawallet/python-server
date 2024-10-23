from django.urls import include, path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', include('dashboard.urls.airtime_urls')),
    path('admin/', include('dashboard.urls.equb_urls')),
    path('admin/', include('dashboard.urls.institution_urls')),
    path('admin/', include('dashboard.urls.invitation_urls')),
    path('admin/', include('dashboard.urls.recurring_contract_urls')),
    path('admin/', include('dashboard.urls.saving_urls')),
    path('admin/', include('dashboard.urls.transaction_urls')),
    path('admin/', include('dashboard.urls.transfer_urls')),
    path('admin/', include('dashboard.urls.user_urls')),
    path('admin/', include('dashboard.urls.scheduled_urls')),
    path('admin/', include('dashboard.urls.report_urls')),
    path('admin/', include('dashboard.urls.bill_urls')),
    path('admin/', include('dashboard.urls.lookup_urls')),
    path('admin/', include('dashboard.urls.payout_urls')),
    path('admin/', include('dashboard.urls.kyc_urls')),
    path('admin/', include('dashboard.urls.auth_urls')),
    path('admin/', include('dashboard.urls.dashboard_user_urls')),
    path('admin/admin', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)