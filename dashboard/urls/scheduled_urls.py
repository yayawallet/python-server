from django.urls import path
from ..views import scheduled_views

urlpatterns = [
    path('scheduled-payment/create', scheduled_views.proxy_create_schedule, name='create-schedule'),
    path('scheduled-payment/list', scheduled_views.proxy_schedule_list, name='schedule-list'),
    path('scheduled-payment/archive/<str:id>', scheduled_views.proxy_archive_schedule, name='archive-schedule'),
    path('scheduled-payment/bulk-schedule-import-request', scheduled_views.bulk_schedule_import_request, name='bulk-schedule-import-request'),
    path('scheduled-payment/submit-bulk-schedule-response', scheduled_views.submit_bulk_schedule_response, name='submit-bulk-schedule-response'),
    path('scheduled-payment/scheduled-bulk-requests', scheduled_views.scheduled_bulk_requests, name='scheduled-bulk-requests'),
]