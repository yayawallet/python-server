from django.urls import path
from ..views import saving_views

urlpatterns = [
    path('saving/create', saving_views.proxy_create_saving, name='create-saving'),
    path('saving/withdrawals', saving_views.proxy_withdraw_saving, name='withdraw-saving'),
    path('saving/refund', saving_views.proxy_claim, name='claim'),
]