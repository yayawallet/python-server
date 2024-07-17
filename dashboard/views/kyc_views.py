from adrf.decorators import api_view
from yayawallet_python_sdk.api import kyc
from .stream_response import stream_response
from ..permisssions.async_permission import async_permission_required

@api_view(['GET'])
async def proxy_request_otp(request, fin):
    response = await kyc.request_otp(fin)
    return stream_response(response)

@api_view(['GET'])
async def proxy_get_kyc_details(request, fin, transaction_id, otp):
    response = await kyc.get_kyc_details(fin, transaction_id, otp)
    return stream_response(response)

@api_view(['GET'])
async def proxy_find_by_tin(request, tin):
    response = await kyc.find_by_tin(tin)
    return stream_response(response)

@api_view(['POST'])
async def proxy_find_by_license_number(request, tin):
    data = request.data
    response = await kyc.find_by_license_number(tin, data.get('licenseNumber'))
    return stream_response(response)