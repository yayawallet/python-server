from adrf.decorators import api_view
from rest_framework.response import Response
from ..permisssions.async_permission import async_permission_required
from yayawallet_python_sdk.api import equb
from .stream_response import stream_response
from ..functions.common_functions import get_logged_in_user_profile
from asgiref.sync import sync_to_async

@async_permission_required('auth.create_equb', raise_exception=True)
@api_view(['POST'])
async def proxy_create_equb(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    data = request.data
    response = await equb.create_equb(
        data.get('equb_account'), 
        data.get('title'), 
        data.get('description'), 
        data.get('location'), 
        data.get('latitude'), 
        data.get('longitude'),
        data.get('period'),
        data.get('amount'),
        data.get('private'),
        logged_in_user.api_key
        )
    return stream_response(response)

@async_permission_required('auth.update_equb', raise_exception=True)
@api_view(['POST'])
async def proxy_update_equb(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    data = request.data
    response = await equb.update_equb(
        str(id),
        data.get('title'), 
        data.get('description'), 
        data.get('location'), 
        data.get('latitude'), 
        data.get('longitude'),
        data.get('period'),
        data.get('amount'),
        data.get('private'),
        logged_in_user.api_key
    )
    return stream_response(response)

@api_view(['GET'])
async def proxy_create_new_round_of_equb(request, id):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    response = await equb.create_new_round_of_equb(id, logged_in_user.api_key)
    return stream_response(response)

@api_view(['GET'])
async def proxy_equb_payments(request, id):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    response = await equb.equb_payments(id, logged_in_user.api_key)
    return stream_response(response)

@api_view(['GET'])
async def proxy_equb_rounds_by_id(request, id):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    response = await equb.equb_rounds_by_id(id, logged_in_user.api_key)
    return stream_response(response)

@api_view(['GET'])
async def proxy_equb_rounds_by_name(request, name):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    response = await equb.equb_rounds_by_name(name, logged_in_user.api_key)
    return stream_response(response)

@api_view(['GET'])
async def proxy_list_of_equbs(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    response = await equb.list_of_equbs(logged_in_user.api_key)
    return stream_response(response)

@api_view(['GET'])
async def proxy_find_equbs_by_user(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    response = await equb.find_equbs_by_user(logged_in_user.api_key)
    return stream_response(response)

@api_view(['GET'])
async def proxy_find_equb_by_id(request, id):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    response = await equb.find_equb_by_id(id, logged_in_user.api_key)
    return stream_response(response)

@api_view(['GET'])
async def proxy_find_equb_by_name(request, name):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    response = await equb.find_equb_by_name(name, logged_in_user.api_key)
    return stream_response(response)

@api_view(['GET'])
async def proxy_pay_equb_round(request, id, round, payment):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    response = await equb.pay_equb_round(id, round, payment, logged_in_user.api_key)
    return stream_response(response)

@api_view(['GET'])
async def proxy_find_members_of_equb(request, id):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    response = await equb.find_members_of_equb(id, logged_in_user.api_key)
    return stream_response(response)

@api_view(['GET'])
async def proxy_remove_members_of_equb(request, id):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    response = await equb.remove_members_of_equb(id, logged_in_user.api_key)
    return stream_response(response)

@api_view(['GET'])
async def proxy_join_equb(request, id):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    response = await equb.join_equb(id, logged_in_user.api_key)
    return stream_response(response)

@api_view(['GET'])
async def proxy_leave_equb(request, id):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    response = await equb.leave_equb(id, logged_in_user.api_key)
    return stream_response(response)