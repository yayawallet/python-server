from adrf.decorators import api_view
from yayawallet_python_sdk.api import payout
from .stream_response import stream_response
from ..permisssions.async_permission import async_permission_required

@api_view(['POST'])
async def proxy_cluster_payout(request):
    data = request.data
    response = await payout.cluster_payout(data)
    return stream_response(response)

@api_view(['POST'])
async def proxy_bulk_cluster_payout(request):
    data = request.data
    response = await payout.bulk_cluster_payout(data)
    return stream_response(response)

@api_view(['POST'])
async def proxy_get_payout(request):
    data = request.data
    response = await payout.get_payout(data)
    return stream_response(response)

@api_view(['DELETE'])
async def proxy_delete_payout(request, id):
    response = await payout.delete_payout(id)
    return stream_response(response)