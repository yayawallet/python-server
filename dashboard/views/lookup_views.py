from adrf.decorators import api_view
from yayawallet_python_sdk.api import lookup
from .stream_response import stream_response

@api_view(['GET'])
async def proxy_gender_lookup(request):
    response = await lookup.gender_lookup()
    return stream_response(response)

@api_view(['GET'])
async def proxy_region_lookup(request):
    response = await lookup.region_lookup()
    return stream_response(response)

@api_view(['GET'])
async def proxy_business_categories_lookup(request):
    response = await lookup.business_categories_lookup()
    return stream_response(response)