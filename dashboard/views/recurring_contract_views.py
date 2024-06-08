from adrf.decorators import api_view
from yayawallet_python_sdk.api import recurring_contract
from django.http.response import JsonResponse
from asgiref.sync import sync_to_async
from .stream_response import stream_response
from ..models import FailedImports, ImportedDocuments
from ..serializers.serializers import FailedImportsSerializer
from ..constants import ImportTypes
from django.http import HttpResponseBadRequest
from ..permisssions.async_permission import async_permission_required
import pandas as pd
from dashboard.tasks import import_contract_rows, import_recurring_payment_request_rows
from python_server.celery import app

@api_view(['GET'])
async def proxy_list_all_contracts(request):
    response = await recurring_contract.list_all_contracts()
    return stream_response(response)

@async_permission_required('auth.create_contract', raise_exception=True)
@api_view(['POST'])
async def proxy_create_contract(request):
    data = request.data
    response = await recurring_contract.create_contract(
        data.get('contract_number'),
        data.get('service_type'),
        data.get('customer_account_name'),
        data.get('meta_data')
        )
    return stream_response(response)

@async_permission_required('auth.request_payment', raise_exception=True)
@api_view(['POST'])
async def proxy_request_payment(request):
    data = request.data
    response = await recurring_contract.request_payment(
        data.get('contract_number'),
        data.get('amount'),
        data.get('currency'),
        data.get('cause'),
        data.get('notification_url'),
        data.get('meta_data') 
        )
    return stream_response(response)

@api_view(['GET'])
async def proxy_get_subscriptions(request):
    response = await recurring_contract.get_subscriptions()
    return stream_response(response)

@api_view(['GET'])
async def proxy_get_list_of_payment_requests(request):
    response = await recurring_contract.get_list_of_payment_requests()
    return stream_response(response)

@api_view(['GET'])
async def proxy_approve_payment_request(request, id):
    response = await recurring_contract.approve_payment_request(id)
    return stream_response(response)

@api_view(['GET'])
async def proxy_reject_payment_request(request, id):
    response = await recurring_contract.reject_payment_request(id)
    return stream_response(response)

@api_view(['GET'])
async def proxy_activate_subscription(request, id):
    response = await recurring_contract.activate_subscription(id)
    return stream_response(response)

@api_view(['GET'])
async def proxy_deactivate_subscription(request, id):
    response = await recurring_contract.deactivate_subscription(id)
    return stream_response(response)

@async_permission_required('auth.bulk_import_contract', raise_exception=True)
@api_view(['POST'])
async def bulk_contract_import(request):
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
    instance = ImportedDocuments(file_name=file_name, remark="", import_type=ImportTypes.get('CONTRACT'))    
    await sync_to_async(instance.save)()
    saved_id = instance.uuid
    import_contract_rows.delay(data, saved_id)

    return JsonResponse({"message": "Contract Requests Import in Progress!!"}, safe=False)

def serialize_failed_contracts(failed_contracts):
    serializer = FailedImportsSerializer(failed_contracts, many=True)
    return serializer.data

@async_permission_required('auth.bulk_import_request_payment', raise_exception=True)
@api_view(['POST'])
async def bulk_recurring_payment_request_import(request):
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
    instance = ImportedDocuments(file_name=file_name, remark="", import_type=ImportTypes.get('REQUEST_PAYMENT'))    
    await sync_to_async(instance.save)()
    saved_id = instance.uuid
    import_recurring_payment_request_rows.delay(data, saved_id)

    return JsonResponse({"message": "Recurring Payment Requests Import in Progress!!"}, safe=False)