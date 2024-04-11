from django.urls import path
from ..views import user_views

urlpatterns = [
    path('user/organization', user_views.proxy_get_organization, name='get-organization'),
    path('user/profile', user_views.proxy_get_user, name='get-profile'),
]