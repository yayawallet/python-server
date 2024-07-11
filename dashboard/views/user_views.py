from adrf.decorators import api_view
from yayawallet_python_sdk.api import user
from .stream_response import stream_response
from ..permisssions.async_permission import async_permission_required

@api_view(['GET'])
async def proxy_get_organization(request):
    response = await user.get_organization()
    return stream_response(response)

@api_view(['GET'])
async def proxy_get_user(request):
    response = await user.get_profile()
    return stream_response(response)

@api_view(['POST'])
async def proxy_search_user(request):
    data = request.data
    response = await user.search_user(data.get('query'))
    return stream_response(response)

@async_permission_required('auth.create_user', raise_exception=True)
@api_view(['POST'])
async def proxy_create_customer_user(request):
    data = request.data
    response = await user.create_customer_user(data)
    return stream_response(response)

@async_permission_required('auth.create_user', raise_exception=True)
@api_view(['POST'])
async def proxy_create_business_user(request):
    data = request.data
    response = await user.create_business_user(data)
    return stream_response(response)

@api_view(['GET'])
async def proxy_get_balance(request):
    response = await user.get_balance()
    return stream_response(response)
