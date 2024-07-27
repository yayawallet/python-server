from adrf.decorators import api_view
from rest_framework.response import Response
from ..permisssions.async_permission import async_permission_required
from yayawallet_python_sdk.api import transfer
from .stream_response import stream_response
from ..functions.common_functions import get_logged_in_user, parse_response
from ..models import ActionTrail
from asgiref.sync import sync_to_async
from ..constants import Actions
from django.http.response import JsonResponse

@api_view(['GET'])
async def proxy_get_transfer_list(request):
    page = request.GET.get('p')
    if not page:
        page = "1"
    params = "?p=" + page
    response = await transfer.get_transfer_list(params)
    return stream_response(response)

@async_permission_required('auth.transfer_as_user', raise_exception=True)
@api_view(['POST'])
async def proxy_transfer_as_user(request):
    data = request.data
    response = await transfer.transfer_as_user(
        data.get('institution_code'), 
        data.get('account_number'),
        data.get('amount'),
        data.get('ref_code'),
        data.get('sender_note'),
        data.get('phone')
        )
    
    if response.status_code == 200 or response.status_code == 201:
        parsed_data = parse_response(response)
        
        instance = ActionTrail(
            user_id=await sync_to_async(get_logged_in_user)(request), 
            action_id=parsed_data.get('id'), 
            action_type=Actions.get("TRANSFER")
        )
        await sync_to_async(instance.save)()
        return JsonResponse(parsed_data, safe=False)
    return stream_response(response)

@async_permission_required('auth.external_account_lookup', raise_exception=True)
@api_view(['POST'])
async def proxy_external_account_lookup(request):
    data = request.data
    response = await transfer.external_account_lookup(
        data.get('institution_code'), 
        data.get('account_number')
        )
    return stream_response(response)

@api_view(['POST'])
async def proxy_get_transfer_fee(request):
    data = request.data
    response = await transfer.get_transfer_fee(
        data.get('institution_code'), 
        data.get('amount')
        )
    return stream_response(response)