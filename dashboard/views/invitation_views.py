from adrf.decorators import api_view
from rest_framework.response import Response
from ..permisssions.async_permission import async_permission_required
from yayawallet_python_sdk.api import invitation
from .stream_response import stream_response

@api_view(['GET'])
async def proxy_find_by_inviter(request):
    response = await invitation.find_by_inviter()
    return stream_response(response)

@async_permission_required('auth.create_invitation', raise_exception=True)
@api_view(['POST'])
async def proxy_create_inivitation(request):
    data = request.data
    response = await invitation.create_inivitation(
        data.get('country'),
        data.get('phone'),
        data.get('amount')
        )
    return stream_response(response)

@api_view(['POST'])
async def proxy_verify_invitation(request):
    data = request.data
    response = await invitation.verify_invitation(data.get('invite_hash'))
    return stream_response(response)

@api_view(['DELETE'])
async def proxy_cancel_invite(request, invite_hash):
    response = await invitation.cancel_invite(invite_hash)
    return stream_response(response)