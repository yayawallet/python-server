from adrf.decorators import api_view
from rest_framework.response import Response
from yayawallet_python_sdk.api import invitation

@api_view(['GET'])
async def proxy_find_by_inviter(request):
    response = await invitation.find_by_inviter()
    return Response(response)

@api_view(['POST'])
async def proxy_create_inivitation(request):
    data = request.data
    response = await invitation.create_inivitation(
        data.get('country'),
        data.get('phone'),
        data.get('amount')
        )
    return Response(response)