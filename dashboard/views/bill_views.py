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
from ..functions.common_functions import get_logged_in_user, parse_response, get_dict_by_property_value, get_logged_in_user_profile
from ..models import ActionTrail, BillSlice
from ..constants import Actions
from django.contrib.postgres.aggregates import ArrayAgg

@async_permission_required('auth.create_bill', raise_exception=True)
@api_view(['POST'])
async def proxy_create_bill(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    data = request.data
    response = await bill.create_bill(
        data.get('client_yaya_account'), 
        data.get('customer_yaya_account'), 
        data.get('amount'), 
        data.get('start_at'), 
        data.get('due_at'), 
        data.get('customer_id'),
        data.get('bill_id'),
        data.get('bill_code'),
        data.get('bill_season'),
        data.get('cluster'),
        data.get('description'),
        data.get('phone'),
        data.get('email'),
        data.get('details'),
        logged_in_user.api_key
        )
    
    if response.status_code == 200 or response.status_code == 201:
        parsed_data = parse_response(response)
        
        instance = ActionTrail(
            user_id=await sync_to_async(get_logged_in_user)(request), 
            action_id=parsed_data.get('id'), 
            action_type=Actions.get("BILL_ACTION")
        )
        await sync_to_async(instance.save)()
        return JsonResponse(parsed_data, safe=False)
        
    return stream_response(response)

@async_permission_required('auth.create_bulk_bill', raise_exception=True)
@api_view(['POST'])
async def proxy_create_bulk_bill(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
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
    import_bill_rows.delay(data, saved_id, logged_in_user.api_key)

    return JsonResponse({"message": "Bill Payments Import in Progress!!"}, safe=False)

@api_view(['GET'])
async def proxy_bulk_bill_status(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    page = request.GET.get('p')
    if not page:
        page = "1"
    params = "?p=" + page
    response = await bill.bulk_bill_status(params, logged_in_user.api_key)
    parsed_content = parse_response(response)
    result = await sync_to_async(
        lambda: list(
            BillSlice.objects.values('imported_document_id').annotate(
                slice_upload_ids=ArrayAgg('slice_upload_id')
            )
        )
    )()
    merged_response = []
    for item in result:
        imported_document_id = item['imported_document_id']
        slice_upload_ids = item['slice_upload_ids']
        document_report = {
            "id": imported_document_id,
            "failed_records": 0,
            "imported_records": 0,
            "submitted_records": 0,
            "status": "DONE",
            "createdAt": "",
        }
        for id in slice_upload_ids:
            slice_report = get_dict_by_property_value(parsed_content.get("data"), "id", id)
            document_report['failed_records'] = document_report['failed_records'] + slice_report['failed_records']
            document_report['imported_records'] = document_report['imported_records'] + slice_report['imported_records']
            document_report['submitted_records'] = document_report['submitted_records'] + slice_report['submitted_records']
            document_report['createdAt'] = slice_report['createdAt']

        merged_response.append(document_report)

    return JsonResponse(merged_response, safe=False)

@async_permission_required('auth.update_bill', raise_exception=True)
@api_view(['POST'])
async def proxy_update_bill(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    data = request.data
    response = await bill.update_bill(
        data.get('client_yaya_account'), 
        data.get('customer_yaya_account'), 
        data.get('amount'), 
        data.get('start_at'), 
        data.get('due_at'), 
        data.get('customer_id'),
        data.get('bill_id'),
        data.get('bill_code'),
        data.get('bill_season'),
        data.get('cluster'),
        data.get('description'),
        data.get('phone'),
        data.get('email'),
        data.get('details'),
        logged_in_user.api_key
        )
    return stream_response(response)


@api_view(['POST'])
async def proxy_bill_list(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    data = request.data
    page = request.GET.get('p')
    if not page:
        page = "1"
    params = "?p=" + page
    response = await bill.bulk_bill_list(data.get('client_yaya_account'), params, logged_in_user.api_key)
    return stream_response(response)

@api_view(['POST'])
async def proxy_bill_find(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    data = request.data
    response = await bill.bulk_bill_find(data.get('client_yaya_account'), data.get('bill_id'), logged_in_user.api_key)
    return stream_response(response)