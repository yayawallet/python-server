from django.urls import path
from ..views import airtime_views

urlpatterns = [
    path('airtime/buy', airtime_views.proxy_buy_airtime, name='buy-airtime'),
    path('airtime/', airtime_views.proxy_list_recharges, name='list-recharges'),
]