from django.urls import path
from ..views import scheduled_views

urlpatterns = [
    path('scheduled-payment/create', scheduled_views.proxy_create_schedule, name='create-schedule'),
    path('scheduled-payment/list', scheduled_views.proxy_schedule_list, name='schedule-list'),
    path('scheduled-payment/archive/<str:id>', scheduled_views.proxy_archive_schedule, name='archive-schedule'),
]