from adrf.decorators import api_view
from rest_framework.response import Response
from yayawallet_python_sdk.api import airtime
from .stream_response import stream_response

@api_view(['POST'])
async def proxy_buy_airtime(request):
    data = request.data
    response = await airtime.buy_airtime(
        data.get('phone'), 
        data.get('amount')
        )
    return stream_response(response)

@api_view(['GET'])
async def proxy_list_recharges(request):
    response = await airtime.list_recharges()
    return stream_response(response)