from adrf.decorators import api_view
from rest_framework.response import Response
from yayawallet_python_sdk.api import institution
from .stream_response import stream_response
from asgiref.sync import sync_to_async
from ..functions.common_functions import get_logged_in_user_profile

@api_view(['POST'])
async def proxy_list_institution(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    data = request.data
    response = await institution.list_institution(
        data.get('country'),
        logged_in_user.api_key
        )
    return stream_response(response)