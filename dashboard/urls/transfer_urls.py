from django.urls import path
from ..views import transfer_views

urlpatterns = [
    path('transfer', transfer_views.proxy_get_transfer_list, name='get-transfer-list'),
    path('transfer/send', transfer_views.proxy_transfer_as_user, name='transfer-as-user'),
    path('transfer/lookup-external', transfer_views.proxy_external_account_lookup, name='external-account-lookup'),
    path('transfer/fee', transfer_views.proxy_get_transfer_fee, name='get-transfer-fee'),
]