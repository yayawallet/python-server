from adrf.decorators import api_view
from ..permisssions.async_permission import async_permission_required
from yayawallet_python_sdk.api import transaction
from .stream_response import stream_response

@api_view(['GET'])
async def proxy_get_transaction_list_by_user(request):
    response = await transaction.get_transaction_list_by_user(None)
    return stream_response(response)

@async_permission_required('auth.can_transfer_money', raise_exception=True)
@api_view(['POST'])
async def proxy_create_transaction(request):
    data = request.data
    response = await transaction.create_transaction(
        data.get('receiver'), 
        data.get('amount'),
        data.get('cause'),
        data.get('meta_data')
        )
    return stream_response(response)

@api_view(['POST'])
async def proxy_transaction_fee(request):
    data = request.data
    response = await transaction.transaction_fee(
        data.get('receiver'), 
        data.get('amount')
        )
    return stream_response(response)

@api_view(['POST'])
async def proxy_generate_qr_url(request):
    data = request.data
    response = await transaction.generate_qr_url(
        data.get('amount'), 
        data.get('cause')
        )
    return stream_response(response)

@api_view(['GET'])
async def proxy_get_transaction_by_id(request, id):
    response = await transaction.get_transaction_by_id(id)
    return stream_response(response)

@api_view(['POST'])
async def proxy_search_transaction(request):
    data = request.data
    response = await transaction.search_transaction(
        data.get('query')
        )
    return stream_response(response)