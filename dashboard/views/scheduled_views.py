from adrf.decorators import api_view
from yayawallet_python_sdk.api import scheduled
from .stream_response import stream_response
from adrf.decorators import api_view
from django.http.response import JsonResponse
from asgiref.sync import sync_to_async
from ..permisssions.async_permission import async_permission_required
from django.http import HttpResponseBadRequest
from ..models import ImportedDocuments
import pandas as pd
from dashboard.tasks import import_scheduled_rows
from ..constants import ImportTypes
import jwt
from django.contrib.auth.models import User
from ..functions.common_functions import get_logged_in_user, parse_response, get_logged_in_user_profile
from ..models import ActionTrail
from ..constants import Actions

@async_permission_required('auth.create_schedule', raise_exception=True)
@api_view(['POST'])
async def proxy_create_schedule(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    data = request.data
    response = await scheduled.create(
        data.get('account_number'), 
        data.get('amount'), 
        data.get('reason'), 
        data.get('recurring'), 
        data.get('start_at'), 
        data.get('meta_data'),
        logged_in_user.api_key
        )
    
    if response.status_code == 200 or response.status_code == 201:
        parsed_data = parse_response(response)
        
        instance = ActionTrail(
            user_id=await sync_to_async(get_logged_in_user)(request), 
            action_id=parsed_data.get('id'), 
            action_type=Actions.get("SCHEDULED_ACTION")
        )
        await sync_to_async(instance.save)()
        return JsonResponse(parsed_data, safe=False)
        
    return stream_response(response)

@api_view(['GET'])
async def proxy_schedule_list(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    page = request.GET.get('p')
    if not page:
        page = "1"
    params = "?p=" + page
    response = await scheduled.get_list(params, logged_in_user.api_key)
    return stream_response(response)

@api_view(['GET'])
async def proxy_archive_schedule(request, id):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    response = await scheduled.archive(id, logged_in_user.api_key)
    return stream_response(response)
    
@async_permission_required('auth.bulk_schedule_import', raise_exception=True)
@api_view(['POST'])
async def bulk_schedule_import(request):
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
        import_type=ImportTypes.get('SCHEDULED'), 
        failed_count=0, 
        successful_count=0, 
        on_queue_count=len(data),
        user_id=logged_in_user
    )
    await sync_to_async(instance.save)()
    saved_id = instance.uuid
    import_scheduled_rows.delay(data, saved_id, logged_in_user_profile.api_key)

    return JsonResponse({"message": "Scheduled Payments Import in Progress!!"}, safe=False)
