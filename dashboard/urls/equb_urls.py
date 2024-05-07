from django.urls import path
from ..views import equb_views

urlpatterns = [
    path('equb/create', equb_views.proxy_create_equb, name='create-equb'),
    path('equb/update/<str:id>', equb_views.proxy_update_equb, name='update-equb'),
    path('equb/create-new-round/<str:id>', equb_views.proxy_create_new_round_of_equb, name='create-new-round-of equb'),
    path('equb/payments/<str:id>', equb_views.proxy_equb_payments, name='equb-payments'),
    path('equb/rounds/<str:id>', equb_views.proxy_equb_rounds_by_id, name='equb-round-by-id'),
    path('equb/rounds/by-name/<str:name>', equb_views.proxy_equb_rounds_by_name, name='equb-round-by-name'),
    path('equb/public', equb_views.proxy_list_of_equbs, name='list-of-equbs'),
    path('equb/find-by-user', equb_views.proxy_find_equbs_by_user, name='find-equbs-by-user'),
    path('equb/find/<str:id>', equb_views.proxy_find_equb_by_id, name='find-equb-by-id'),
    path('equb/find-by-name/<str:name>', equb_views.proxy_find_equb_by_name, name='find-equb-by-name'),
    path('equb/pay/<str:id>/<str:round>/<str:payment>', equb_views.proxy_pay_equb_round, name='pay-equb-round'),
    path('equb/<str:id>/members', equb_views.proxy_find_members_of_equb, name='find-members-of-equb'),
    path('equb/remove-member/<str:id>', equb_views.proxy_remove_members_of_equb, name='remove-members-of-equb'),
    path('equb/<str:id>/join', equb_views.proxy_join_equb, name='join-equb'),
    path('equb/<str:id>/leave', equb_views.proxy_leave_equb, name='leave-equb') 
]