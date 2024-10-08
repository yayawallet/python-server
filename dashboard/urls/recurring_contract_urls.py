from django.urls import path
from ..views import recurring_contract_views

urlpatterns = [
    path('recurring-contract/list', recurring_contract_views.proxy_list_all_contracts, name='list-of-all-contracts'),
    path('recurring-contract/contract-request', recurring_contract_views.contract_request, name='contract-request'),
    path('recurring-contract/submit-contract-response', recurring_contract_views.submit_contract_response, name='submit-contract-response'),
    path('recurring-contract/contract-requests', recurring_contract_views.contract_requests, name='contract-requests'),
    path('recurring-contract/payment-request', recurring_contract_views.payment_request, name='payment-request'),
    path('recurring-contract/submit-payment-request-response', recurring_contract_views.submit_payment_request_response, name='submit-payment-request-response'),
    path('recurring-contract/payment-requests', recurring_contract_views.payment_requests, name='payment-requests'),
    path('recurring-contract/payment-my-requests', recurring_contract_views.payment_my_requests, name='payment-my-requests'),
    path('recurring-contract/subscriptions', recurring_contract_views.proxy_get_subscriptions, name='get-subscriptions'),
    path('recurring-contract/payment-requests', recurring_contract_views.proxy_get_list_of_payment_requests, name='get-list-of-payment-requests'),
    path('recurring-contract/approve-payment/<str:id>', recurring_contract_views.proxy_approve_payment_request, name='approve-payment-request'),
    path('recurring-contract/reject-payment/<str:id>', recurring_contract_views.proxy_reject_payment_request, name='reject-payment-request'),
    path('recurring-contract/activate/<str:id>', recurring_contract_views.proxy_activate_subscription, name='activate-subscription'),
    path('recurring-contract/deactivate/<str:id>', recurring_contract_views.proxy_deactivate_subscription, name='deactivate-subscription'),
    path('recurring-contract/bulk-contract-import-request', recurring_contract_views.bulk_contract_import_request, name='bulk_contract_import_request'),
    path('recurring-contract/submit-bulk-contract-response', recurring_contract_views.submit_bulk_contract_response, name='submit-bulk-contract-response'),
    path('recurring-contract/contract-bulk-requests', recurring_contract_views.contract_bulk_requests, name='contract-bulk-requests'),
    path('recurring-contract/bulk-import-payment-request', recurring_contract_views.bulk_import_payment_request, name='bulk-import-payment-request'),
    path('recurring-contract/submit-bulk-payment-request-response', recurring_contract_views.submit_bulk_payment_request_response, name='submit-bulk-payment-request-response'),
    path('recurring-contract/request-payment-bulk-requests', recurring_contract_views.request_payment_bulk_requests, name='request-payment-bulk-requests'),
]