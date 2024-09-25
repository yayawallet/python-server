from adrf.decorators import api_view
from yayawallet_python_sdk.api import scheduled
from .stream_response import stream_response
from adrf.decorators import api_view
from django.http.response import JsonResponse
from asgiref.sync import sync_to_async
from ..permisssions.async_permission import async_permission_required
from django.http import HttpResponseBadRequest
from ..models import ImportedDocuments, ApprovalRequest, RejectedRequest
import pandas as pd
from dashboard.tasks import import_scheduled_rows
from ..constants import ImportTypes, Requests
import jwt
from django.db.models.functions import Cast
from django.db.models.fields import IntegerField
from django.db.models.fields.json import KeyTextTransform
from django.contrib.auth.models import User, Group
from ..functions.common_functions import get_logged_in_user, parse_response, get_logged_in_user_profile, get_logged_in_user_profile_instance, get_paginated_response, get_paginated_bulk_response, add_approver_sync, get_approver_objects
from ..models import ActionTrail, UserProfile, ApproverRule
from ..constants import Actions, Approve, Reject, Pending
from django.db.models import Q
from rest_framework.response import Response
from ..serializers.serializers import ApprovalRequestSerializer
from django.core.exceptions import ObjectDoesNotExist

@async_permission_required('auth.schedule_request', raise_exception=True)
@api_view(['POST'])
async def schedule_request(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    logged_in_user_profile=await sync_to_async(get_logged_in_user_profile_instance)(request)

    data = request.data
    amount = data.get("amount")

    approval_request = ApprovalRequest(
        request_json=data,
        requesting_user=logged_in_user_profile,
        request_type=Requests.get('SCHEDULED'), 
    )

    approver_objects = await sync_to_async(get_approver_objects)(logged_in_user_profile, approval_request, amount)
    approvers_count = len(approver_objects)

    if approvers_count == 0:
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
    
    await sync_to_async(approval_request.save)()

    await sync_to_async(add_approver_sync)(approval_request, approver_objects)

    return JsonResponse({"message": "Scheduled Payments Request created!!"}, safe=False)

@async_permission_required('auth.approval_scheduled', raise_exception=True)
@api_view(['POST'])
async def submit_scheduled_response(request):
    auth_header = request.headers.get('Authorization')
    token = auth_header.split(' ')[1]
    decoded_token = jwt.decode(jwt=token, algorithms=["HS256"], options={'verify_signature':False})
    logged_in_user = await sync_to_async(User.objects.get)(id=decoded_token.get("user_id"))
    logged_in_user_profile = await sync_to_async(get_logged_in_user_profile)(request)
    approval_request = await sync_to_async(ApprovalRequest.objects.get)(uuid=request.POST.get('approval_request_id'))
    
    is_approved = await sync_to_async(lambda: approval_request.approved_by.filter(id=logged_in_user.id).exists())()
    is_rejected = await sync_to_async(lambda: approval_request.rejected_by.filter(user=logged_in_user).exists())()
    
    if is_approved:
        return Response({"message": "User has already approved this request."}, status=400)
    
    if is_rejected:
        return Response({"message": "User has already rejected this request."}, status=400)

    if request.POST.get('response') == Approve:
        data = approval_request.request_json
        amount = data.get("amount")

        await sync_to_async(approval_request.approved_by.add)(logged_in_user)
        await sync_to_async(approval_request.save)()

        requester = await sync_to_async(lambda: approval_request.requesting_user)()

        approver_objects = await sync_to_async(get_approver_objects)(requester, approval_request, amount)
        approvers_count = len(approver_objects)
        approved_users = await sync_to_async(approval_request.approved_by.all)()
        approved_users_count = await sync_to_async(approved_users.count)()

        if approvers_count == approved_users_count:
            data = approval_request.request_json
            meta_data = {}
            response = await scheduled.create(
                data.get('account_number'), 
                data.get('amount'), 
                data.get('reason'), 
                data.get('recurring'), 
                data.get('start_at'), 
                meta_data,
                logged_in_user_profile.api_key
                )
            
            if response.status_code == 200 or response.status_code == 201:
                parsed_data = parse_response(response)
                requesting_user_object = await sync_to_async(lambda: approval_request.requesting_user.user)()
                
                instance = ActionTrail(
                    user_id=requesting_user_object, 
                    action_id=parsed_data.get('id'), 
                    action_type=Actions.get("SCHEDULED_ACTION")
                )
                await sync_to_async(instance.save)()
                approval_request.is_successful = True
                await sync_to_async(approval_request.save)()
                return JsonResponse(parsed_data, safe=False)
            
            approval_request.is_successful = False
            await sync_to_async(approval_request.save)()
            return stream_response(response)
        else:
            serialized_data = await sync_to_async(get_single_approval_request_serialized_data)(approval_request)
            return Response(serialized_data)
    else:
        rejected_request_instance = RejectedRequest(
            user=logged_in_user, 
            rejection_reason=request.POST.get('rejection_reason'),
        )
        await sync_to_async(rejected_request_instance.save)()
        await sync_to_async(approval_request.rejected_by.add)(rejected_request_instance)
        await sync_to_async(approval_request.save)()
        serialized_data = await sync_to_async(get_single_approval_request_serialized_data)(approval_request)
        return Response(serialized_data)

def get_approval_request_serialized_data(db_results):
    serializer = ApprovalRequestSerializer(db_results, many=True)
    return serializer.data

def get_single_approval_request_serialized_data(db_results):
    serializer = ApprovalRequestSerializer(db_results)
    return serializer.data

@async_permission_required('auth.scheduled_requests', raise_exception=True)
@api_view(['GET'])
async def scheduled_requests(request):
    logged_in_user=await sync_to_async(get_logged_in_user)(request)
    logged_in_user_profile=await sync_to_async(get_logged_in_user_profile_instance)(request)

    approver_group = await sync_to_async(Group.objects.get)(name='Approver')
    is_approver = await sync_to_async(lambda: logged_in_user.groups.filter(id=approver_group.id).exists())()

    if not is_approver:
        queryset = await sync_to_async(lambda: ApprovalRequest.objects.filter(
            requesting_user__id=logged_in_user_profile.id,
            request_type=Requests.get('SCHEDULED')
        ).order_by('-updated_at').all())()
        paginated_response = await sync_to_async(get_paginated_response)(request, queryset)
        return JsonResponse(paginated_response)
    else:
        get_pending = request.GET.get('status') == Pending

        approve_threshold = 0
        try:
            approver_rule = await sync_to_async(ApproverRule.objects.get)(user=logged_in_user_profile)
            approve_threshold = approver_rule.approve_threshold
        except ObjectDoesNotExist:
            pass
        
        base_queryset = await sync_to_async(lambda: ApprovalRequest.objects.annotate(
            amount_value=Cast(KeyTextTransform('amount', 'request_json'), IntegerField())
        ).filter(
            requesting_user__api_key=logged_in_user_profile.api_key,
            request_type=Requests.get('SCHEDULED'),
            amount_value__gte=approve_threshold,
            created_at__gte=logged_in_user.date_joined
        ).order_by('-updated_at').all())()

        if get_pending:
            queryset = await sync_to_async(lambda: [req for req in base_queryset if not req.rejected_by.exists() and logged_in_user not in req.approved_by.all()])()
        else:
            queryset = base_queryset

        paginated_response = await sync_to_async(get_paginated_response)(request, queryset)
        return JsonResponse(paginated_response)
        

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

@async_permission_required('auth.bulk_schedule_request', raise_exception=True)
@api_view(['POST'])
async def bulk_schedule_import_request(request):
    logged_in_user_profile=await sync_to_async(get_logged_in_user_profile_instance)(request)
    logged_in_user=await sync_to_async(get_logged_in_user)(request)
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

    approval_request = ApprovalRequest(
        requesting_user=logged_in_user_profile,
        request_type=Requests.get('SCHEDULED_BULK_IMPORT'), 
        file=uploaded_file, 
        remark=request.POST.get('remark'), 
    )

    approver_objects = await sync_to_async(get_approver_objects)(logged_in_user_profile, approval_request)
    approvers_count = len(approver_objects)

    if approvers_count == 0:
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
        import_scheduled_rows.delay(data, saved_id, logged_in_user_profile.api_key.api_key)

        return JsonResponse({"message": "Scheduled Payments Import in Progress!!"}, safe=False)
    
    await sync_to_async(approval_request.save)()
    await sync_to_async(add_approver_sync)(approval_request, approver_objects)

    return JsonResponse({"message": "Scheduled Payments Import Request created!!"}, safe=False)
    
@async_permission_required('auth.approval_bulk_schedule_import', raise_exception=True)
@api_view(['POST'])
async def submit_bulk_schedule_response(request):
    logged_in_user_profile=await sync_to_async(get_logged_in_user_profile)(request)
    uploaded_file = request.FILES.get('file')
    auth_header = request.headers.get('Authorization')
    token = auth_header.split(' ')[1]
    decoded_token = jwt.decode(jwt=token, algorithms=["HS256"], options={'verify_signature':False})
    logged_in_user = await sync_to_async(User.objects.get)(id=decoded_token.get("user_id"))
    approval_request = await sync_to_async(ApprovalRequest.objects.get)(uuid=request.POST.get('approval_request_id'))
    remark=approval_request.remark
    uploaded_file = approval_request.file

    is_approved = await sync_to_async(lambda: approval_request.approved_by.filter(id=logged_in_user.id).exists())()
    is_rejected = await sync_to_async(lambda: approval_request.rejected_by.filter(user=logged_in_user).exists())()
    
    if is_approved:
        return Response({"message": "User has already approved this request."}, status=400)
    
    if is_rejected:
        return Response({"message": "User has already rejected this request."}, status=400)

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
    
    if request.POST.get('response') == Approve:
        await sync_to_async(approval_request.approved_by.add)(logged_in_user)
        await sync_to_async(approval_request.save)()

        requester = await sync_to_async(lambda: approval_request.requesting_user)()

        approver_objects = await sync_to_async(get_approver_objects)(requester, approval_request)
        approvers_count = len(approver_objects)
        approved_users = await sync_to_async(approval_request.approved_by.all)()
        approved_users_count = await sync_to_async(approved_users.count)()

        if approvers_count == approved_users_count:
            instance = ImportedDocuments(
                file_name=file_name, 
                remark=remark, 
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
        else:
            serialized_data = await sync_to_async(get_single_approval_request_serialized_data)(approval_request)
            return Response(serialized_data)
    else:
        rejected_request_instance = RejectedRequest(
            user=logged_in_user, 
            rejection_reason=request.POST.get('rejection_reason'),
        )
        await sync_to_async(rejected_request_instance.save)()
        await sync_to_async(approval_request.rejected_by.add)(rejected_request_instance)
        await sync_to_async(approval_request.save)()
        serialized_data = await sync_to_async(get_single_approval_request_serialized_data)(approval_request)
        return Response(serialized_data)

def get_approval_request_serialized_data(db_results):
    serializer = ApprovalRequestSerializer(db_results, many=True)
    return serializer.data

def get_single_approval_request_serialized_data(db_results):
    serializer = ApprovalRequestSerializer(db_results)
    return serializer.data

@async_permission_required('auth.bulk_scheduled_requests', raise_exception=True)
@api_view(['GET'])
async def scheduled_bulk_requests(request):
    logged_in_user=await sync_to_async(get_logged_in_user)(request)
    logged_in_user_profile=await sync_to_async(get_logged_in_user_profile_instance)(request)

    approver_group = await sync_to_async(Group.objects.get)(name='Approver')
    is_approver = await sync_to_async(lambda: logged_in_user.groups.filter(id=approver_group.id).exists())()

    if not is_approver:
        queryset = await sync_to_async(lambda: ApprovalRequest.objects.filter(
            requesting_user__id=logged_in_user_profile.id,
            request_type=Requests.get('SCHEDULED_BULK_IMPORT')
        ).order_by('-updated_at').all())()
        paginated_response = await sync_to_async(get_paginated_bulk_response)(request, queryset)
        return JsonResponse(paginated_response)
    else:
        get_pending = request.GET.get('status') == Pending
        
        base_queryset = await sync_to_async(lambda: ApprovalRequest.objects.filter(
            requesting_user__api_key=logged_in_user_profile.api_key,
            request_type=Requests.get('SCHEDULED_BULK_IMPORT'),
            created_at__gte=logged_in_user.date_joined
        ).order_by('-updated_at').all())()

        if get_pending:
            queryset = await sync_to_async(lambda: [req for req in base_queryset if not req.rejected_by.exists() and logged_in_user not in req.approved_by.all()])()
        else:
            queryset = base_queryset

        paginated_response = await sync_to_async(get_paginated_bulk_response)(request, queryset)
        return JsonResponse(paginated_response)