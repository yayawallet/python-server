from django.urls import path
from ..views import transaction_views

urlpatterns = [
    path('transaction/find-by-user', transaction_views.proxy_get_transaction_list_by_user, name='get-transaction-list-by-user'),
    path('transaction/create', transaction_views.proxy_create_transaction, name='create-transaction'),
    path('transaction/fee', transaction_views.proxy_transaction_fee, name='transaction-fee'),
    path('transaction/qr-generate', transaction_views.proxy_generate_qr_url, name='generate-qr-url'),
    path('transaction/find/<str:id>', transaction_views.proxy_get_transaction_by_id, name='get-transaction-by-id'),
    path('transaction/search', transaction_views.proxy_search_transaction, name='search-transaction'),
]