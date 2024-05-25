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
from io import TextIOWrapper
import csv

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
    if not uploaded_file or (not uploaded_file.name.endswith('.csv') and not uploaded_file.name.endswith('.xlsx')):
        return HttpResponseBadRequest("The uploaded file is not a CSV or XLSX file.")

    instances = []
    with TextIOWrapper(uploaded_file, encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            instance = Scheduled(account_number=row[0], amount=row[1], reason=row[2], recurring=row[3], start_at=row[4], meta_data=json.dumps(row[5]), json_object=json.dumps(row), uploaded=False)
            instances.append(instance)
    await sync_to_async(Scheduled.objects.bulk_create)(instances)
    import_scheduled_rows.delay()

    return JsonResponse({"message": "Scheduled Payments Import in Progress!!"}, safe=False)
