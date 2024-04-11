from django.urls import path
from ..views import institution_views

urlpatterns = [
    path('financial-institution/list', institution_views.proxy_list_institution, name='list-of-institution'),
]