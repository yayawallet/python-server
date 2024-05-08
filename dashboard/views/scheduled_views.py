from adrf.decorators import api_view
from rest_framework.response import Response
from yayawallet_python_sdk.api import scheduled

@api_view(['POST'])
async def proxy_create_schedule(request):
    data = request.data
    response = await scheduled.create(
        data.get('account_number'), 
        data.get('amount'), 
        data.get('reason'), 
        data.get('recurring'), 
        data.get('start_at'), 
        data.get('meta_data')
        )
    return Response(response)

@api_view(['GET'])
async def proxy_schedule_list(request):
    response = await scheduled.get_list()
    return Response(response)

@api_view(['GET'])
async def proxy_archive_schedule(request):
    response = await scheduled.archive()
    return Response(response)