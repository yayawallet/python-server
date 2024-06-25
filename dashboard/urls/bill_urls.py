from django.urls import path
from ..views import equb_views

urlpatterns = [
    path('bill/create', equb_views.proxy_create_equb, name='create-bill'),
    path('bulkimport/bills', equb_views.proxy_update_equb, name='create-bulk-bill'),
    path('bulkimport/', equb_views.proxy_create_new_round_of_equb, name='bulk-bill-status'),
    path('bill/update', equb_views.proxy_equb_payments, name='update-bill'),
]