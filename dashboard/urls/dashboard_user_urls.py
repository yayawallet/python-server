from django.urls import path
from ..views import dashboard_user_views

urlpatterns = [
    path('user/change-password/', dashboard_user_views.proxy_change_password, name='change-password'),
    path('user/me/', dashboard_user_views.proxy_get_dashboard_user, name='get-dashboard-user'),
]