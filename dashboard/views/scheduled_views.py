from adrf.decorators import api_view
from yayawallet_python_sdk.api import scheduled
from .stream_response import stream_response
from adrf.decorators import api_view
from django.http.response import JsonResponse
from asgiref.sync import sync_to_async
from django.http import HttpResponseBadRequest
from ..models import ImportedDocuments
import pandas as pd
from dashboard.tasks import import_scheduled_rows
from ..constants import ImportTypes

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
    uploaded_file = request.FILES.get('file')
    if not uploaded_file:
        return HttpResponseBadRequest("No file uploaded.")
    
    file_name = uploaded_file.name

    if file_name.endswith('.csv'):
        try:
            df = pd.read_csv(uploaded_file)
        except Exception as e:
            return HttpResponseBadRequest(f"Error reading CSV file: {e}")
    elif file_name.endswith(('.xls', '.xlsx')):
        try:
            df = pd.read_excel(uploaded_file)
        except Exception as e:
            return HttpResponseBadRequest(f"Error reading Excel file: {e}")
    else:
        return HttpResponseBadRequest("The uploaded file is not a CSV or Excel file.")

    try:
        data = df.to_dict(orient='records')
    except Exception as e:
        return HttpResponseBadRequest(f"Error converting file to JSON: {e}")
    instance = ImportedDocuments(file_name=file_name, remark="", import_type=ImportTypes.get('SCHEDULED'))    
    await sync_to_async(instance.save)()
    saved_id = instance.uuid
    import_scheduled_rows.delay(data, saved_id)

    return JsonResponse({"message": "Scheduled Payments Import in Progress!!"}, safe=False)
