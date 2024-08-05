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
import jwt
from django.contrib.auth.models import User
from ..functions.common_functions import get_logged_in_user, parse_response, get_logged_in_user_profile
from ..models import ActionTrail
from ..constants import Actions

@api_view(['GET'])
async def proxy_list_all_contracts(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    response = await recurring_contract.list_all_contracts(logged_in_user.api_key)
    return stream_response(response)

@async_permission_required('auth.create_contract', raise_exception=True)
@api_view(['POST'])
async def proxy_create_contract(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    data = request.data
    response = await recurring_contract.create_contract(
        data.get('contract_number'),
        data.get('service_type'),
        data.get('customer_account_name'),
        data.get('meta_data'),
        logged_in_user.api_key
        )
    if response.status_code == 200 or response.status_code == 201:
        parsed_data = parse_response(response)
        
        instance = ActionTrail(
            user_id=await sync_to_async(get_logged_in_user)(request), 
            action_id=parsed_data.get('contract_id'), 
            action_type=Actions.get("CONTRACT_ACTION")
        )
        await sync_to_async(instance.save)()
        return JsonResponse(parsed_data, safe=False)
    

    return stream_response(response)

@async_permission_required('auth.request_payment', raise_exception=True)
@api_view(['POST'])
async def proxy_request_payment(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    data = request.data
    response = await recurring_contract.request_payment(
        data.get('contract_number'),
        data.get('amount'),
        data.get('currency'),
        data.get('cause'),
        data.get('notification_url'),
        data.get('meta_data'),
        logged_in_user.api_key
        )
    return stream_response(response)

@api_view(['GET'])
async def proxy_get_subscriptions(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    response = await recurring_contract.get_subscriptions(logged_in_user.api_key)
    return stream_response(response)

@api_view(['GET'])
async def proxy_get_list_of_payment_requests(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    response = await recurring_contract.get_list_of_payment_requests(logged_in_user.api_key)
    return stream_response(response)

@api_view(['GET'])
async def proxy_approve_payment_request(request, id):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    response = await recurring_contract.approve_payment_request(id, logged_in_user.api_key)
    return stream_response(response)

@api_view(['GET'])
async def proxy_reject_payment_request(request, id):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    response = await recurring_contract.reject_payment_request(id, logged_in_user.api_key)
    return stream_response(response)

@api_view(['GET'])
async def proxy_activate_subscription(request, id):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    response = await recurring_contract.activate_subscription(id, logged_in_user.api_key)
    return stream_response(response)

@api_view(['GET'])
async def proxy_deactivate_subscription(request, id):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    response = await recurring_contract.deactivate_subscription(id, logged_in_user.api_key)
    return stream_response(response)

@async_permission_required('auth.bulk_import_contract', raise_exception=True)
@api_view(['POST'])
async def bulk_contract_import(request):
    logged_in_user_profile=await sync_to_async(get_logged_in_user_profile)(request)
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
        import_type=ImportTypes.get('CONTRACT'), 
        failed_count=0, 
        successful_count=0, 
        on_queue_count=len(data),
        user_id=logged_in_user
    )    
    await sync_to_async(instance.save)()
    saved_id = instance.uuid
    import_contract_rows.delay(data, saved_id, logged_in_user_profile.api_key)

    return JsonResponse({"message": "Contract Requests Import in Progress!!"}, safe=False)

def serialize_failed_contracts(failed_contracts):
    serializer = FailedImportsSerializer(failed_contracts, many=True)
    return serializer.data

@async_permission_required('auth.bulk_import_request_payment', raise_exception=True)
@api_view(['POST'])
async def bulk_recurring_payment_request_import(request):
    logged_in_user_profile=await sync_to_async(get_logged_in_user_profile)(request)
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
        import_type=ImportTypes.get('REQUEST_PAYMENT'), 
        failed_count=0, 
        successful_count=0, 
        on_queue_count=len(data),
        user_id=logged_in_user
    )    
    await sync_to_async(instance.save)()
    saved_id = instance.uuid
    import_recurring_payment_request_rows.delay(data, saved_id, logged_in_user_profile.api_key)

    return JsonResponse({"message": "Recurring Payment Requests Import in Progress!!"}, safe=False)