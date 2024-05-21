from adrf.decorators import api_view
from rest_framework.response import Response
from yayawallet_python_sdk.api import institution
from .stream_response import stream_response

@api_view(['POST'])
async def proxy_list_institution(request):
    data = request.data
    response = await institution.list_institution(
        data.get('country'),
        )
    return stream_response(response)