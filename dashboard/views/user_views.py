from adrf.decorators import api_view
from yayawallet_python_sdk.api import user
from .stream_response import stream_response
from ..permisssions.async_permission import async_permission_required
from ..functions.common_functions import get_logged_in_user_profile
from asgiref.sync import sync_to_async

@api_view(['GET'])
async def proxy_get_organization(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    response = await user.get_organization(logged_in_user.api_key)
    return stream_response(response)

@api_view(['GET'])
async def proxy_get_user(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    response = await user.get_profile(logged_in_user.api_key)
    return stream_response(response)

@api_view(['POST'])
async def proxy_search_user(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    data = request.data
    response = await user.search_user(data.get('query'), logged_in_user.api_key)
    return stream_response(response)

@async_permission_required('auth.create_user', raise_exception=True)
@api_view(['POST'])
async def proxy_create_customer_user(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    data = request.data
    response = await user.create_customer_user(data, logged_in_user.api_key)
    return stream_response(response)

@async_permission_required('auth.create_user', raise_exception=True)
@api_view(['POST'])
async def proxy_create_business_user(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    data = request.data
    response = await user.create_business_user(data, logged_in_user.api_key)
    return stream_response(response)

@api_view(['GET'])
async def proxy_get_balance(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    response = await user.get_balance(logged_in_user.api_key)
    return stream_response(response)

@async_permission_required('auth.create_user', raise_exception=True)
@api_view(['POST'])
async def proxy_update_user(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    data = request.data
    response = await user.update_user(
        data.get('account_name'), 
        data.get('name'), 
        data.get('gender'), 
        data.get('region'), 
        data.get('location'), 
        data.get('date_of_birth'),
        data.get('sms_notification_enable'), 
        data.get('email_notification_enable'), 
        data.get('app_notification_enable'),
        logged_in_user.api_key
    )
    return stream_response(response)
