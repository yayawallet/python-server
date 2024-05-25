from django.urls import path
from ..views import airtime_views

urlpatterns = [
    path('airtime/buy', airtime_views.proxy_buy_airtime, name='buy-airtime'),
    path('package/buy', airtime_views.proxy_buy_airtime, name='buy-package  '),
    path('airtime/list', airtime_views.proxy_list_recharges, name='list-recharges'),
    path('airtime/packages', airtime_views.proxy_list_packages, name='list-airtime'),
]