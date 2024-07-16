from django.urls import path
from ..views import kyc_views

urlpatterns = [
    path('kyc/fayda/request-otp/<str:fin>', kyc_views.proxy_request_otp, name='request-otp'),
    path('kyc/fayda/get-kyc-details/<str:fin>/<str:transaction_id>/<str:otp>', kyc_views.proxy_get_kyc_details, name='get-kyc-details'),
    path('kyc/etrade/find-by-tin/<str:tin>', kyc_views.proxy_find_by_tin, name='find-by-tin'),
    path('kyc/etrade/find-by-license-number/<str:tin>', kyc_views.proxy_find_by_license_number, name='find-by-license-number'),
]