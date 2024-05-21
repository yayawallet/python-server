from adrf.decorators import api_view
from rest_framework.response import Response
from yayawallet_python_sdk.api import user
from .stream_response import stream_response

@api_view(['GET'])
async def proxy_get_organization(request):
    response = await user.get_organization()
    print(response)
    return stream_response(response)

@api_view(['GET'])
async def proxy_get_user(request):
    response = await user.get_profile()
    print(response)
    return stream_response(response)