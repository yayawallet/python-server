from adrf.decorators import api_view
from rest_framework.response import Response
from yayawallet_python_sdk.api import user

@api_view(['GET'])
async def proxy_get_organization(request):
    response = await user.get_organization()
    print(response)
    return Response(response)

@api_view(['GET'])
async def proxy_get_user(request):
    response = await user.get_profile()
    print(response)
    return Response(response)