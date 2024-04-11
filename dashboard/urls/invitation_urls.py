from django.urls import path
from ..views import invitation_views

urlpatterns = [
    path('invitation/find-by-inviter', invitation_views.proxy_find_by_inviter, name='find-by-inviter'),
    path('invitation/create', invitation_views.proxy_create_inivitation, name='create-invitation'),
]