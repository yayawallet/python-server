from adrf.decorators import api_view
from rest_framework.response import Response
from yayawallet_python_sdk.api import user
from .stream_response import stream_response

@api_view(['GET'])
async def proxy_get_organization(request):
    response = await user.get_organization()
    return Response(response)

@api_view(['GET'])
async def proxy_get_user(request):
    response = await user.get_profile()
    return Response(response)

@api_view(['POST'])
async def proxy_search_user(request):
    data = request.data
    response = await user.search_user(data.get('query'))
    return Response(response)
