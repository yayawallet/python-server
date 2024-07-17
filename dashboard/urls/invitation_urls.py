from django.urls import path
from ..views import invitation_views

urlpatterns = [
    path('invitation/find-by-inviter', invitation_views.proxy_find_by_inviter, name='find-by-inviter'),
    path('invitation/create', invitation_views.proxy_create_inivitation, name='create-invitation'),
    path('invitation/find-by-hash', invitation_views.proxy_verify_invitation, name='verify-invitation'),
    path('invitation/cancel/<str:invite_hash>', invitation_views.proxy_cancel_invite, name='cancel-invitation'),
    path('invitation/otp', invitation_views.proxy_get_otp, name='get-otp'),
]