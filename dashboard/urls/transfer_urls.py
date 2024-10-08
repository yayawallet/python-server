from django.urls import path
from ..views import transfer_views

urlpatterns = [
    path('transfer/list', transfer_views.proxy_get_transfer_list, name='get-transfer-list'),
    path('transfer/transfer-request', transfer_views.transfer_request, name='transfer-request'),
    path('transfer/submit-transfer-response', transfer_views.submit_transfer_response, name='submit-transfer-response'),
    path('transfer/transfer-requests', transfer_views.transfer_requests, name='transfer-requests'),
    path('transfer/lookup-external', transfer_views.proxy_external_account_lookup, name='external-account-lookup'),
    path('transfer/fee', transfer_views.proxy_get_transfer_fee, name='get-transfer-fee'),
]