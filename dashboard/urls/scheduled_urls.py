from django.urls import path
from ..views import scheduled_views

urlpatterns = [
    path('scheduled-payment/schedule-request', scheduled_views.schedule_request, name='schedule-request'),
    path('scheduled-payment/submit-scheduled-response', scheduled_views.submit_scheduled_response, name='submit-scheduled-response'),
    path('scheduled-payment/scheduled-requests', scheduled_views.scheduled_requests, name='scheduled-requests'),
    path('scheduled-payment/scheduled-my-requests', scheduled_views.scheduled_my_requests, name='scheduled-my-requests'),
    path('scheduled-payment/list', scheduled_views.proxy_schedule_list, name='schedule-list'),
    path('scheduled-payment/archive/<str:id>', scheduled_views.proxy_archive_schedule, name='archive-schedule'),
    path('scheduled-payment/bulk-schedule-import-request', scheduled_views.bulk_schedule_import_request, name='bulk-schedule-import-request'),
    path('scheduled-payment/submit-bulk-schedule-response', scheduled_views.submit_bulk_schedule_response, name='submit-bulk-schedule-response'),
    path('scheduled-payment/scheduled-bulk-requests', scheduled_views.scheduled_bulk_requests, name='scheduled-bulk-requests'),
    path('scheduled-payment/scheduled-my-bulk-requests', scheduled_views.scheduled_my_bulk_requests, name='scheduled-my-bulk-requests'),
]