from adrf.decorators import api_view
from rest_framework.response import Response
from yayawallet_python_sdk.api import transfer

@api_view(['GET'])
async def proxy_get_transfer_list(request):
    response = await transfer.get_transfer_list()
    return Response(response)

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
    return Response(response)

@api_view(['POST'])
async def proxy_external_account_lookup(request):
    data = request.data
    response = await transfer.external_account_lookup(
        data.get('institution_code'), 
        data.get('account_number')
        )
    return Response(response)

@api_view(['POST'])
async def proxy_get_transfer_fee(request):
    data = request.data
    response = await transfer.get_transfer_fee(
        data.get('institution_code'), 
        data.get('amount')
        )
    return Response(response)