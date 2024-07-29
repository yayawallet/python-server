from adrf.decorators import api_view
from yayawallet_python_sdk.api import lookup
from .stream_response import stream_response
from asgiref.sync import sync_to_async
from ..functions.common_functions import get_logged_in_user_profile

@api_view(['GET'])
async def proxy_gender_lookup(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    response = await lookup.gender_lookup(logged_in_user.api_key)
    return stream_response(response)

@api_view(['GET'])
async def proxy_region_lookup(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    response = await lookup.region_lookup(logged_in_user.api_key)
    return stream_response(response)

@api_view(['GET'])
async def proxy_business_categories_lookup(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    response = await lookup.business_categories_lookup(logged_in_user.api_key)
    return stream_response(response)