from django.urls import path
from ..views import recurring_contract_views

urlpatterns = [
    path('recurring-contract', recurring_contract_views.proxy_list_all_contracts, name='list-of-all-contracts'),
    path('recurring-contract/create', recurring_contract_views.proxy_create_contract, name='create-contract'),    
    path('recurring-contract/request-payment', recurring_contract_views.proxy_request_payment, name='request-payment'),
    path('recurring-contract/subscriptions', recurring_contract_views.proxy_get_subscriptions, name='get-subscriptions'),
    path('recurring-contract/payment-requests', recurring_contract_views.proxy_get_list_of_payment_requests, name='get-list-of-payment-requests'),
    path('recurring-contract/approve-payment/<str:id>', recurring_contract_views.proxy_approve_payment_request, name='approve-payment-request'),
    path('recurring-contract/reject-payment/<str:id>', recurring_contract_views.proxy_reject_payment_request, name='reject-payment-request'),
    path('recurring-contract/activate/<str:id>', recurring_contract_views.proxy_activate_subscription, name='activate-subscription'),
    path('recurring-contract/deactivate/<str:id>', recurring_contract_views.proxy_deactivate_subscription, name='deactivate-subscription'),
]