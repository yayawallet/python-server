from adrf.decorators import api_view
from rest_framework.response import Response
from yayawallet_python_sdk.api import recurring_contract
from django.http.response import JsonResponse
from asgiref.sync import sync_to_async
from .stream_response import stream_response
from ..models import FailedContract
from ..serializers.serializers import FailedContractSerializer
from django.http import HttpResponseBadRequest
import pandas as pd
from dashboard.tasks import import_contract_rows, import_recurring_payment_request_rows
from python_server.celery import app

@api_view(['GET'])
async def proxy_list_all_contracts(request):
    response = await recurring_contract.list_all_contracts()
    return stream_response(response)

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
    import_contract_rows.delay(data)

    return JsonResponse({"message": "Contract Requests Import in Progress!!"}, safe=False)

def serialize_failed_contracts(failed_contracts):
    serializer = FailedContractSerializer(failed_contracts, many=True)
    return serializer.data


@api_view(['GET'])
async def failed_contract_imports(request):
    failed_contracts = await sync_to_async(FailedContract.objects.filter)()
    failed_contracts_data = await sync_to_async(serialize_failed_contracts)(failed_contracts)
    
    return JsonResponse(failed_contracts_data, safe=False)

@api_view(['GET'])
async def contract_import_status(request):
    data = app.control.inspect().active()
    for key, tasks in data.items():
        for task in tasks:
            if task.get('type') and task.get('type') == "dashboard.tasks.import_contract_rows":
                return JsonResponse({'status': 'Contract import in progress!'}, safe=False)
    return JsonResponse({'status': 'No contract import running!'}, safe=False)

@api_view(['POST'])
async def bulk_recurring_payment_request_import(request):
    import_recurring_payment_request_rows.delay(request)

    return JsonResponse({"message": "Recurring Payment Requests Import in Progress!!"}, safe=False)