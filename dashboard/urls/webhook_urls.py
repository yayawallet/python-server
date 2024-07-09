from django.urls import path
from ..views import user_views

urlpatterns = [
    path('webhook/transaction', user_views.proxy_get_organization, name='get-organization'),
]