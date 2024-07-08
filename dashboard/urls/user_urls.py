from django.urls import path
from ..views import user_views

urlpatterns = [
    path('user/organization', user_views.proxy_get_organization, name='get-organization'),
    path('user/profile', user_views.proxy_get_user, name='get-profile'),
    path('user/search', user_views.proxy_search_user, name='get-profile'),
    path('user/register', user_views.proxy_create_customer_user, name='create-customer'),
    path('user/register-business', user_views.proxy_create_business_user, name='create-business'),
]