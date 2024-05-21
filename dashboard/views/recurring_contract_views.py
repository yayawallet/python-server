from adrf.decorators import api_view
from rest_framework.response import Response
from yayawallet_python_sdk.api import recurring_contract
from .stream_response import stream_response

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