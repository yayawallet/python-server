from django.urls import path
from ..views import airtime_views

urlpatterns = [
    path('airtime/airtime-request', airtime_views.airtime_request, name='airtime-request'),
    path('airtime/submit-airtime-response', airtime_views.submit_airtime_response, name='submit-airtime-response'),
    path('airtime/airtime-requests', airtime_views.airtime_requests, name='airtime-requests'),
    path('airtime/airtime-my-requests', airtime_views.airtime_my_requests, name='airtime-my-requests'),
    path('airtime/package-request', airtime_views.package_request, name='package-request'),
    path('airtime/submit-package-response', airtime_views.submit_package_response, name='submit-package-response'),
    path('airtime/package-requests', airtime_views.package_requests, name='package-requests'),
    path('airtime/package-my-requests', airtime_views.package_my_requests, name='package-my-requests'),
    path('airtime/list', airtime_views.proxy_list_recharges, name='list-recharges'),
    path('airtime/packages', airtime_views.proxy_list_packages, name='list-airtime'),
]