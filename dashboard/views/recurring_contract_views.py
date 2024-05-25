from adrf.decorators import api_view
from rest_framework.response import Response
from yayawallet_python_sdk.api import recurring_contract
from django.http.response import JsonResponse
from asgiref.sync import sync_to_async
from .stream_response import stream_response
from django.http import HttpResponseBadRequest
from ..models import Contract, RecurringPaymentRequest
import json
from dashboard.tasks import import_contract_rows, import_recurring_payment_request_rows

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
    uploaded_file = request.FILES['file']
    if not uploaded_file.name.endswith('.json'):
        return HttpResponseBadRequest("The uploaded file is not a JSON file.")
    instances = []
    json_data = uploaded_file.read().decode('utf-8')
    data = json.loads(json_data)
    for row in data:
        instance = Contract(contract_number=row.get('contract_number'), service_type=row.get('service_type'), customer_account_name=row.get('customer_account_name'), meta_data=json.dumps(row.get('meta_data')), json_object=json.dumps(row), uploaded=False)
        instances.append(instance)
    await sync_to_async(Contract.objects.bulk_create)(instances)
    import_contract_rows.delay()

    return JsonResponse({"message": "Contract Requests Import in Progress!!"}, safe=False)

@api_view(['POST'])
async def bulk_recurring_payment_request_import(request):
    uploaded_file = request.FILES['file']
    if not uploaded_file.name.endswith('.json'):
        return HttpResponseBadRequest("The uploaded file is not a JSON file.")
    instances = []
    json_data = uploaded_file.read().decode('utf-8')
    data = json.loads(json_data)
    for row in data:
        instance = RecurringPaymentRequest(contract_number=row.get('contract_number'), amount=row.get('amount'), currency=row.get('currency'), cause=row.get('cause'), notification_url=row.get('notification_url'), meta_data=json.dumps(row.get('meta_data')), json_object=json.dumps(row), uploaded=False)
        instances.append(instance)
    await sync_to_async(RecurringPaymentRequest.objects.bulk_create)(instances)
    import_recurring_payment_request_rows.delay()

    return JsonResponse({"message": "Recurring Payment Requests Import in Progress!!"}, safe=False)