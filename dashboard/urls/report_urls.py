from django.urls import path
from ..views import report_views

urlpatterns = [
    path('report/list', report_views.proxy_report_list, name='report-list'),
    path('report/details/<str:id>', report_views.proxy_report_detail, name='report-detail'),
]