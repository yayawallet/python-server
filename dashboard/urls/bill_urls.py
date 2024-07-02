from django.urls import path
from ..views import bill_views

urlpatterns = [
    path('bill/create', bill_views.proxy_create_bill, name='create-bill'),
    path('bulkimport/bills', bill_views.proxy_create_bulk_bill, name='create-bulk-bill'),
    path('bulkimport/list', bill_views.proxy_bulk_bill_status, name='bulk-bill-status'),
    path('bill/update', bill_views.proxy_update_bill, name='update-bill'),
    path('bill/list', bill_views.proxy_bill_list, name='bill-list'),
    path('bill/find', bill_views.proxy_bill_find, name='bill-find'),
]