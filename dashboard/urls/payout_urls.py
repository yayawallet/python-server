from django.urls import path
from ..views import payout_views

urlpatterns = [
    path('payout-method/create', payout_views.proxy_cluster_payout, name='cluster-payout'),
    path('bulkimport/payout-methods', payout_views.proxy_bulk_cluster_payout, name='bulk-cluster-payout'),
    path('payout-method/list', payout_views.proxy_get_payout, name='get-payout'),
    path('payout-method/delete/<str:id>', payout_views.proxy_delete_payout, name='delete-payout'),
]