from adrf.decorators import api_view
from rest_framework.response import Response
from ..permisssions.async_permission import async_permission_required
from yayawallet_python_sdk.api import invitation
from .stream_response import stream_response
from asgiref.sync import sync_to_async
from ..functions.common_functions import get_logged_in_user_profile

@api_view(['GET'])
async def proxy_find_by_inviter(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    response = await invitation.find_by_inviter(logged_in_user.api_key)
    return stream_response(response)

@async_permission_required('auth.create_invitation', raise_exception=True)
@api_view(['POST'])
async def proxy_create_inivitation(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    data = request.data
    response = await invitation.create_inivitation(
        data.get('country'),
        data.get('phone'),
        data.get('amount'),
        logged_in_user.api_key
        )
    return stream_response(response)

@api_view(['POST'])
async def proxy_verify_invitation(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    data = request.data
    response = await invitation.verify_invitation(data.get('invite_hash'), logged_in_user.api_key)
    return stream_response(response)

@api_view(['DELETE'])
async def proxy_cancel_invite(request, invite_hash):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    response = await invitation.cancel_invite(invite_hash, logged_in_user.api_key)
    return stream_response(response)

@async_permission_required('auth.get_invitation_otp', raise_exception=True)
@api_view(['POST'])
async def proxy_get_otp(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    data = request.data
    response = await invitation.get_otp(
        data.get('country'),
        data.get('phone'),
        data.get('invite_hash'),
        logged_in_user.api_key
        )
    return stream_response(response)