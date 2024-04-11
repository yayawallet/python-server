from adrf.decorators import api_view
from rest_framework.response import Response
from yayawallet_python_sdk.api import transaction

@api_view(['GET'])
async def proxy_get_transaction_list_by_user(request):
    response = await transaction.get_transaction_list_by_user()
    return Response(response)

@api_view(['POST'])
async def proxy_create_transaction(request):
    data = request.data
    response = await transaction.create_transaction(
        data.get('receiver'), 
        data.get('amount'),
        data.get('cause'),
        data.get('meta_data')
        )
    return Response(response)

@api_view(['POST'])
async def proxy_transaction_fee(request):
    data = request.data
    response = await transaction.transaction_fee(
        data.get('receiver'), 
        data.get('amount')
        )
    return Response(response)

@api_view(['POST'])
async def proxy_generate_qr_url(request):
    data = request.data
    response = await transaction.generate_qr_url(
        data.get('amount'), 
        data.get('cause')
        )
    return Response(response)

@api_view(['GET'])
async def proxy_get_transaction_by_id(request, id):
    response = await transaction.get_transaction_by_id(id)
    return Response(response)

@api_view(['POST'])
async def proxy_search_transaction(request):
    data = request.data
    response = await transaction.search_transaction(
        data.get('query')
        )
    return Response(response)