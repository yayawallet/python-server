from adrf.decorators import api_view
from rest_framework.response import Response
from ..permisssions.async_permission import async_permission_required
from yayawallet_python_sdk.api import transfer
from .stream_response import stream_response

@api_view(['GET'])
async def proxy_get_transfer_list(request):
    response = await transfer.get_transfer_list()
    return stream_response(response)

@async_permission_required('auth.transfer_as_user', raise_exception=True)
@api_view(['POST'])
async def proxy_transfer_as_user(request):
    data = request.data
    response = await transfer.transfer_as_user(
        data.get('institution_code'), 
        data.get('account_number'),
        data.get('amount'),
        data.get('ref_code'),
        data.get('sender_note'),
        data.get('phone')
        )
    return stream_response(response)

@async_permission_required('auth.external_account_lookup', raise_exception=True)
@api_view(['POST'])
async def proxy_external_account_lookup(request):
    data = request.data
    response = await transfer.external_account_lookup(
        data.get('institution_code'), 
        data.get('account_number')
        )
    return stream_response(response)

@api_view(['POST'])
async def proxy_get_transfer_fee(request):
    data = request.data
    response = await transfer.get_transfer_fee(
        data.get('institution_code'), 
        data.get('amount')
        )
    return stream_response(response)