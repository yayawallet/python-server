from adrf.decorators import api_view
from rest_framework.response import Response
from ..permisssions.async_permission import async_permission_required
from yayawallet_python_sdk.api import bill
from .stream_response import stream_response

@async_permission_required('auth.create_bill', raise_exception=True)
@api_view(['POST'])
async def proxy_create_bill(request):
    data = request.data
    response = await bill.create_bill(
        data.get('client_yaya_account'), 
        data.get('customer_yaya_account'), 
        data.get('amount'), 
        data.get('start_at'), 
        data.get('due_at'), 
        data.get('customer_id'),
        data.get('bill_id'),
        data.get('fwd_institution'),
        data.get('fwd_account_number'),
        data.get('description'),
        data.get('phone'),
        data.get('email'),
        data.get('details')
        )
    return stream_response(response)

@async_permission_required('auth.create_bulk_bill', raise_exception=True)
@api_view(['POST'])
async def proxy_create_bulk_bill(request):
    data = request.data
    response = await bill.create_bulk_bill(data)
    return stream_response(response)

@api_view(['GET'])
async def proxy_bulk_bill_status(request):
    response = await bill.bulk_bill_status()
    return stream_response(response)

@async_permission_required('auth.update_bill', raise_exception=True)
@api_view(['POST'])
async def proxy_update_bill(request):
    data = request.data
    response = await bill.update_bill(
        data.get('client_yaya_account'), 
        data.get('customer_yaya_account'), 
        data.get('amount'),  
        data.get('customer_id'),
        data.get('bill_id'),
        data.get('phone'),
        data.get('email'),
        )
    return stream_response(response)