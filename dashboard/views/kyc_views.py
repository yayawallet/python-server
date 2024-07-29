from adrf.decorators import api_view
from yayawallet_python_sdk.api import kyc
from .stream_response import stream_response
from ..permisssions.async_permission import async_permission_required
from asgiref.sync import sync_to_async
from ..functions.common_functions import get_logged_in_user_profile

@api_view(['GET'])
async def proxy_request_otp(request, fin):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    response = await kyc.request_otp(fin, logged_in_user.api_key)
    return stream_response(response)

@api_view(['GET'])
async def proxy_get_kyc_details(request, fin, transaction_id, otp):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    response = await kyc.get_kyc_details(fin, transaction_id, otp, logged_in_user.api_key)
    return stream_response(response)

@api_view(['GET'])
async def proxy_find_by_tin(request, tin):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    response = await kyc.find_by_tin(tin, logged_in_user.api_key)
    return stream_response(response)

@api_view(['POST'])
async def proxy_find_by_license_number(request, tin):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    data = request.data
    response = await kyc.find_by_license_number(tin, data.get('licenseNumber'), logged_in_user.api_key)
    return stream_response(response)