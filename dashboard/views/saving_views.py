from adrf.decorators import api_view
from rest_framework.response import Response
from yayawallet_python_sdk.api import saving
from .stream_response import stream_response

@api_view(['POST'])
async def proxy_create_saving(request):
    data = request.data
    response = await saving.create_saving(
        data.get('amount'), 
        data.get('action')
        )
    return stream_response(response)

@api_view(['GET'])
async def proxy_withdraw_saving(request):
    response = await saving.withdraw_saving()
    return stream_response(response)

@api_view(['POST'])
async def proxy_claim(request):
    data = request.data
    response = await saving.claim(
        data.get('request_ids')
        )
    return stream_response(response)