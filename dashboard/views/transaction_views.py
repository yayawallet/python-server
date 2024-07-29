from adrf.decorators import api_view
from ..permisssions.async_permission import async_permission_required
from yayawallet_python_sdk.api import transaction
from .stream_response import stream_response
from ..models import ActionTrail
from asgiref.sync import sync_to_async
from ..functions.common_functions import get_logged_in_user, parse_response, get_logged_in_user_profile
from django.http.response import JsonResponse
from ..constants import Actions

@api_view(['GET'])
async def proxy_get_transaction_list_by_user(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    page = request.GET.get('p')
    if not page:
        page = "1"
    params = "?p=" + page
    response = await transaction.get_transaction_list_by_user(params, logged_in_user.api_key)
    return stream_response(response)

@async_permission_required('auth.can_transfer_money', raise_exception=True)
@api_view(['POST'])
async def proxy_create_transaction(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    data = request.data
    response = await transaction.create_transaction(
        data.get('receiver'), 
        data.get('amount'),
        data.get('cause'),
        data.get('meta_data'),
        logged_in_user.api_key
        )
    
    if response.status_code == 200 or response.status_code == 201:
        parsed_data = parse_response(response)

        instance = ActionTrail(
            user_id=await sync_to_async(get_logged_in_user)(request), 
            action_id=parsed_data.get('transaction_id'), 
            action_type=Actions.get("TRANSACTION")
        )
        await sync_to_async(instance.save)()
        return JsonResponse(parsed_data, safe=False)
    return stream_response(response)

@api_view(['POST'])
async def proxy_transaction_fee(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    data = request.data
    response = await transaction.transaction_fee(
        data.get('receiver'), 
        data.get('amount'),
        logged_in_user.api_key
        )
    return stream_response(response)

@async_permission_required('auth.generate_qr_url', raise_exception=True)
@api_view(['POST'])
async def proxy_generate_qr_url(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    data = request.data
    response = await transaction.generate_qr_url(
        data.get('amount'), 
        data.get('cause'),
        logged_in_user.api_key
        )
    return stream_response(response)

@api_view(['GET'])
async def proxy_get_transaction_by_id(request, id):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    response = await transaction.get_transaction_by_id(id, logged_in_user.api_key)
    return stream_response(response)

@api_view(['POST'])
async def proxy_search_transaction(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    data = request.data
    response = await transaction.search_transaction(
        data.get('query'),
        logged_in_user.api_key
        )
    return stream_response(response)