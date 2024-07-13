from adrf.decorators import api_view
from yayawallet_python_sdk.api import payout
from .stream_response import stream_response
from django.http.response import JsonResponse
from django.http import HttpResponseBadRequest
import pandas as pd
import jwt
from django.contrib.auth.models import User
from ..models import ImportedDocuments
from asgiref.sync import sync_to_async
from ..constants import ImportTypes
from ..permisssions.async_permission import async_permission_required
from dashboard.tasks import import_payout_rows

@async_permission_required('auth.create_payout', raise_exception=True)
@api_view(['POST'])
async def proxy_cluster_payout(request):
    data = request.data
    response = await payout.cluster_payout(data)
    return stream_response(response)

@async_permission_required('auth.create_bulk_payout', raise_exception=True)
@api_view(['POST'])
async def proxy_bulk_cluster_payout(request):
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
        import_type=ImportTypes.get('PAYOUT'), 
        failed_count=0, 
        successful_count=0, 
        on_queue_count=len(data),
        user_id=logged_in_user
    )
    await sync_to_async(instance.save)()
    saved_id = instance.uuid
    import_payout_rows.delay(data, saved_id)

    return JsonResponse({"message": "Payout Import in Progress!!"}, safe=False)

@api_view(['POST'])
async def proxy_get_payout(request):
    data = request.data
    response = await payout.get_payout(data)
    return stream_response(response)

@api_view(['DELETE'])
async def proxy_delete_payout(request, id):
    response = await payout.delete_payout(id)
    return stream_response(response)