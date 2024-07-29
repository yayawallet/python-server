from adrf.decorators import api_view
from rest_framework.response import Response
from ..permisssions.async_permission import async_permission_required
from yayawallet_python_sdk.api import airtime
from .stream_response import stream_response
from ..functions.common_functions import get_logged_in_user, parse_response, get_logged_in_user_profile
from ..models import ActionTrail
from asgiref.sync import sync_to_async
from ..constants import Actions
from django.http.response import JsonResponse

@async_permission_required('auth.buy_airtime', raise_exception=True)
@api_view(['POST'])
async def proxy_buy_airtime(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    data = request.data
    response = await airtime.buy_airtime(
        data.get('phone'), 
        data.get('amount'),
        logged_in_user.api_key
        )
    
    if response.status_code == 200 or response.status_code == 201:
        parsed_data = parse_response(response)
        user_id = await sync_to_async(get_logged_in_user)(request)
        
        instance = ActionTrail(
            user_id=user_id, 
            action_id=parsed_data.get('id'), 
            action_type=Actions.get("AIRTIME")
        )
        await sync_to_async(instance.save)()
        return JsonResponse(parsed_data, safe=False)
    
    return stream_response(response)

@async_permission_required('auth.buy_package', raise_exception=True)
@api_view(['POST'])
async def proxy_buy_package(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    data = request.data
    response = await airtime.buy_package(
        data.get('phone'), 
        data.get('package'),
        logged_in_user.api_key
        )
    
    if response.status_code == 200 or response.status_code == 201:
        parsed_data = parse_response(response).get('data')
        
        instance = ActionTrail(
            user_id=await sync_to_async(get_logged_in_user)(request), 
            action_id=parsed_data.get('id'), 
            action_type=Actions.get("PACKAGE")
        )
        await sync_to_async(instance.save)()
        return JsonResponse(parsed_data, safe=False)
    return stream_response(response)

@api_view(['GET'])
async def proxy_list_recharges(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    response = await airtime.list_recharges(logged_in_user.api_key)
    return stream_response(response)

@api_view(['POST'])
async def proxy_list_packages(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    data = request.data
    response = await airtime.list_packages(
        data.get('phone'),
        logged_in_user.api_key
        )
    return stream_response(response)