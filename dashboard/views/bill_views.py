from adrf.decorators import api_view
from rest_framework.response import Response
from ..permisssions.async_permission import async_permission_required
from yayawallet_python_sdk.api import bill
from django.http import HttpResponseBadRequest
from .stream_response import stream_response
import jwt
import pandas as pd
from ..models import ImportedDocuments
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from ..constants import ImportTypes
from django.http.response import JsonResponse
from dashboard.tasks import import_bill_rows

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
    
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'row_number'}, inplace=True)
    df['row_number'] += 2

    try:
        data = df.to_dict(orient='records')
    except Exception as e:
        return HttpResponseBadRequest(f"Error converting file to JSON: {e}")
    auth_header = request.headers.get('Authorization')
    token = auth_header.split(' ')[1]
    decoded_token = jwt.decode(jwt=token, algorithms=["HS256"], options={'verify_signature':False})
    logged_in_user = await sync_to_async(User.objects.get)(id=decoded_token.get("user_id"))
    instance = ImportedDocuments(
        file_name=file_name, 
        remark=request.POST.get('remark'), 
        import_type=ImportTypes.get('BILL'), 
        failed_count=0, 
        successful_count=0, 
        on_queue_count=len(data),
        user_id=logged_in_user
    )
    await sync_to_async(instance.save)()
    saved_id = instance.uuid
    import_bill_rows.delay(data, saved_id)

    return JsonResponse({"message": "Bill Payments Import in Progress!!"}, safe=False)

@api_view(['GET'])
async def proxy_bulk_bill_status(request):
    data = request.data
    response = await bill.bulk_bill_status(data.get("client_yaya_account"))
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