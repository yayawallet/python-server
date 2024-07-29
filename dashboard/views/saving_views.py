from adrf.decorators import api_view
from rest_framework.response import Response
from ..permisssions.async_permission import async_permission_required
from yayawallet_python_sdk.api import saving
from .stream_response import stream_response
from asgiref.sync import sync_to_async
from ..functions.common_functions import get_logged_in_user_profile

@async_permission_required('auth.create_saving', raise_exception=True)
@api_view(['POST'])
async def proxy_create_saving(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    data = request.data
    response = await saving.create_saving(
        data.get('amount'), 
        data.get('action'),
        logged_in_user.api_key
        )
    return stream_response(response)

@api_view(['GET'])
async def proxy_withdraw_saving(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    response = await saving.withdraw_saving(logged_in_user.api_key)
    return stream_response(response)

@async_permission_required('auth.claim', raise_exception=True)
@api_view(['POST'])
async def proxy_claim(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    data = request.data
    response = await saving.claim(
        data.get('request_ids'),
        logged_in_user.api_key
        )
    return stream_response(response)