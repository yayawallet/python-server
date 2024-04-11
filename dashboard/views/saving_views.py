from adrf.decorators import api_view
from rest_framework.response import Response
from yayawallet_python_sdk.api import saving

@api_view(['POST'])
async def proxy_create_saving(request):
    data = request.data
    response = await saving.create_saving(
        data.get('amount'), 
        data.get('action')
        )
    return Response(response)

@api_view(['GET'])
async def proxy_withdraw_saving(request):
    response = await saving.withdraw_saving()
    return Response(response)

@api_view(['POST'])
async def proxy_claim(request):
    data = request.data
    response = await saving.claim(
        data.get('request_ids')
        )
    return Response(response)