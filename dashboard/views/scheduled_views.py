from adrf.decorators import api_view
from yayawallet_python_sdk.api import scheduled
from .stream_response import stream_response
from adrf.decorators import api_view
from django.http.response import JsonResponse
from asgiref.sync import sync_to_async
from django.http import HttpResponseBadRequest
from ..models import Scheduled
import json
from dashboard.tasks import import_scheduled_rows

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
    return stream_response(response)

@api_view(['GET'])
async def proxy_schedule_list(request):
    response = await scheduled.get_list()
    return stream_response(response)

@api_view(['GET'])
async def proxy_archive_schedule(request, id):
    response = await scheduled.archive(id)
    return stream_response(response)
    
@api_view(['POST'])
async def bulk_schedule_import(request):
    uploaded_file = request.FILES['file']
    if not uploaded_file.name.endswith('.json'):
        return HttpResponseBadRequest("The uploaded file is not a JSON file.")
    instances = []
    json_data = uploaded_file.read().decode('utf-8')
    data = json.loads(json_data)
    for row in data:
        instance = Scheduled(account_number=row.get('account_number'), amount=row.get('amount'), reason=row.get('reason'), recurring=row.get('recurring'), start_at=row.get('start_at'), meta_data=json.dumps(row.get('meta_data')), json_object=json.dumps(row), uploaded=False)
        instances.append(instance)
    await sync_to_async(Scheduled.objects.bulk_create)(instances)
    import_scheduled_rows.delay()

    return JsonResponse({"message": "Scheduled Payments Import in Progress!!"}, safe=False)
