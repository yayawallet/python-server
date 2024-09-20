from adrf.decorators import api_view
from yayawallet_python_sdk.api import recurring_contract
from django.http.response import JsonResponse
from asgiref.sync import sync_to_async
from .stream_response import stream_response
from ..models import ImportedDocuments, ApprovalRequest, RejectedRequest
from ..serializers.serializers import FailedImportsSerializer
from ..constants import ImportTypes, Requests, Approve
from django.http import HttpResponseBadRequest
from ..permisssions.async_permission import async_permission_required
import pandas as pd
from dashboard.tasks import import_contract_rows, import_recurring_payment_request_rows
from python_server.celery import app
from ..functions.common_functions import get_logged_in_user, parse_response, get_logged_in_user_profile, get_logged_in_user_profile_instance, get_paginated_response, get_paginated_bulk_response, add_approver_sync
import jwt
from django.contrib.auth.models import User, Group
from ..models import ActionTrail, UserProfile, ApproverRule
from ..constants import Actions, Pending
from django.db.models import Q
import json
from rest_framework.response import Response
from ..serializers.serializers import ApprovalRequestSerializer
from django.db.models.functions import Cast
from django.db.models.fields import IntegerField
from django.db.models.fields.json import KeyTextTransform
from django.core.exceptions import ObjectDoesNotExist

@api_view(['GET'])
async def proxy_list_all_contracts(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    response = await recurring_contract.list_all_contracts(logged_in_user.api_key)
    return stream_response(response)

@async_permission_required('auth.contract_request', raise_exception=True)
@api_view(['POST'])
async def contract_request(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    logged_in_user_profile=await sync_to_async(get_logged_in_user_profile_instance)(request)
    data = request.data

    approval_request = ApprovalRequest(
        request_json=json.dumps(data),
        requesting_user=logged_in_user_profile,
        request_type=Requests.get('CONTRACT'), 
    )
    await sync_to_async(approval_request.save)()

    approver_group = await sync_to_async(Group.objects.get)(name='Approver')
    approvers = await sync_to_async(User.objects.filter)(groups=approver_group)
    approvers_user_ids = await sync_to_async(lambda: [user.id for user in approvers])()
    approver_user_profiles = await sync_to_async(lambda: UserProfile.objects.filter(
        user__id__in=approvers_user_ids,
        user__userprofile__api_key=logged_in_user_profile.api_key
    ))()
    approver_objects = await sync_to_async(lambda: [approver_user_profile.user for approver_user_profile in approver_user_profiles])()
    approvers_count = await sync_to_async(approver_user_profiles.count)()

    await sync_to_async(add_approver_sync)(approval_request, approver_objects)

    if approvers_count == 0:
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
                action_id=parsed_data.get('id'), 
                action_type=Actions.get("CONTRACT_ACTION")
            )
            await sync_to_async(instance.save)()
            approval_request.is_successful = True
            await sync_to_async(approval_request.save)()
            return JsonResponse(parsed_data, safe=False)
        
        approval_request.is_successful = False
        await sync_to_async(approval_request.save)() 
        return stream_response(response)

    return JsonResponse({"message": "Contract Request created!!"}, safe=False)

@async_permission_required('auth.approval_contract', raise_exception=True)
@api_view(['POST'])
async def submit_contract_response(request):
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
        await sync_to_async(approval_request.approved_by.add)(logged_in_user)
        await sync_to_async(approval_request.save)()

        approver_group = await sync_to_async(Group.objects.get)(name='Approver')
        approvers = await sync_to_async(User.objects.filter)(groups=approver_group)
        approvers_user_ids = await sync_to_async(lambda: [user.id for user in approvers])()
        approvers_count = await sync_to_async(lambda: UserProfile.objects.filter(
            user__id__in=approvers_user_ids,
            user__userprofile__api_key=approval_request.requesting_user.api_key
        ).count())()

        approved_users = await sync_to_async(approval_request.approved_by.all)()
        approved_users_count = await sync_to_async(approved_users.count)()

        if approvers_count == approved_users_count:
            data = json.loads(approval_request.request_json)
            meta_data = {}
            response = await recurring_contract.create_contract(
                data.get('contract_number'),
                data.get('service_type'),
                data.get('customer_account_name'),
                meta_data,
                logged_in_user_profile.api_key
                )
            
            if response.status_code == 200 or response.status_code == 201:
                parsed_data = parse_response(response)
                requesting_user_object = await sync_to_async(lambda: approval_request.requesting_user.user)()
                
                instance = ActionTrail(
                    user_id=requesting_user_object, 
                    action_id=parsed_data.get('id'), 
                    action_type=Actions.get("CONTRACT_ACTION")
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

@async_permission_required('auth.contract_requests', raise_exception=True)
@api_view(['GET'])
async def contract_requests(request):
    logged_in_user=await sync_to_async(get_logged_in_user)(request)
    logged_in_user_profile=await sync_to_async(get_logged_in_user_profile_instance)(request)

    approver_group = await sync_to_async(Group.objects.get)(name='Approver')
    is_approver = await sync_to_async(lambda: logged_in_user.groups.filter(id=approver_group.id).exists())()

    if not is_approver:
        queryset = await sync_to_async(lambda: ApprovalRequest.objects.filter(
            requesting_user__id=logged_in_user_profile.id,
            request_type=Requests.get('CONTRACT')
        ).order_by('-updated_at').all())()
        paginated_response = await sync_to_async(get_paginated_bulk_response)(request, queryset)
        return JsonResponse(paginated_response)
    else:
        queryset = await sync_to_async(lambda: ApprovalRequest.objects.filter(
            requesting_user__api_key=logged_in_user_profile.api_key,
            request_type=Requests.get('CONTRACT')
        ).order_by('-updated_at').all())()
        paginated_response = await sync_to_async(get_paginated_bulk_response)(request, queryset)
        return JsonResponse(paginated_response)

@async_permission_required('auth.payment_request', raise_exception=True)
@api_view(['POST'])
async def payment_request(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    logged_in_user_profile=await sync_to_async(get_logged_in_user_profile_instance)(request)
    data = request.data

    approval_request = ApprovalRequest(
        request_json=json.dumps(data),
        requesting_user=logged_in_user_profile,
        request_type=Requests.get('REQUEST_PAYMENT'), 
    )
    await sync_to_async(approval_request.save)()

    approver_group = await sync_to_async(Group.objects.get)(name='Approver')
    approvers = await sync_to_async(User.objects.filter)(groups=approver_group)
    approvers_user_ids = await sync_to_async(lambda: [user.id for user in approvers])()
    approver_user_profiles = await sync_to_async(lambda: UserProfile.objects.filter(
        user__id__in=approvers_user_ids,
        user__userprofile__api_key=logged_in_user_profile.api_key
    ))()
    approver_objects = await sync_to_async(lambda: [approver_user_profile.user for approver_user_profile in approver_user_profiles])()
    approvers_count = await sync_to_async(approver_user_profiles.count)()

    await sync_to_async(add_approver_sync)(approval_request, approver_objects)

    if approvers_count == 0:
        response = await recurring_contract.request_payment(
            data.get('contract_number'),
            data.get('amount'),
            data.get('currency'),
            data.get('cause'),
            data.get('notification_url'),
            data.get('meta_data'),
            logged_in_user.api_key
            )
        
        if response.status_code == 200 or response.status_code == 201:
            parsed_data = parse_response(response)
            
            instance = ActionTrail(
                user_id=await sync_to_async(get_logged_in_user)(request), 
                action_id=parsed_data.get('id'), 
                action_type=Actions.get("REQUEST_PAYMENT_ACTION")
            )
            await sync_to_async(instance.save)()
            approval_request.is_successful = True
            await sync_to_async(approval_request.save)()
            return JsonResponse(parsed_data, safe=False)
        
        approval_request.is_successful = False
        await sync_to_async(approval_request.save)() 
        return stream_response(response)

    return JsonResponse({"message": "Payment Request for Approval created!!"}, safe=False)

@async_permission_required('auth.approval_payment_request', raise_exception=True)
@api_view(['POST'])
async def submit_payment_request_response(request):
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
        await sync_to_async(approval_request.approved_by.add)(logged_in_user)
        await sync_to_async(approval_request.save)()

        approver_group = await sync_to_async(Group.objects.get)(name='Approver')
        approvers = await sync_to_async(User.objects.filter)(groups=approver_group)
        approvers_user_ids = await sync_to_async(lambda: [user.id for user in approvers])()
        approvers_count = await sync_to_async(lambda: UserProfile.objects.filter(
            user__id__in=approvers_user_ids,
            user__userprofile__api_key=approval_request.requesting_user.api_key
        ).count())()

        approved_users = await sync_to_async(approval_request.approved_by.all)()
        approved_users_count = await sync_to_async(approved_users.count)()

        if approvers_count == approved_users_count:
            data = json.loads(approval_request.request_json)
            meta_data = {}
            response = await recurring_contract.request_payment(
                data.get('contract_number'),
                data.get('amount'),
                data.get('currency'),
                data.get('cause'),
                data.get('notification_url'),
                meta_data,
                logged_in_user_profile.api_key
                )
            
            if response.status_code == 200 or response.status_code == 201:
                parsed_data = parse_response(response)
                requesting_user_object = await sync_to_async(lambda: approval_request.requesting_user.user)()
                
                instance = ActionTrail(
                    user_id=requesting_user_object, 
                    action_id=parsed_data.get('id'), 
                    action_type=Actions.get("REQUEST_PAYMENT_ACTION")
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

@async_permission_required('auth.payment_requests', raise_exception=True)
@api_view(['GET'])
async def payment_requests(request):
    logged_in_user=await sync_to_async(get_logged_in_user)(request)
    logged_in_user_profile=await sync_to_async(get_logged_in_user_profile_instance)(request)

    approver_group = await sync_to_async(Group.objects.get)(name='Approver')
    is_approver = await sync_to_async(lambda: logged_in_user.groups.filter(id=approver_group.id).exists())()

    if not is_approver:
        queryset = await sync_to_async(lambda: ApprovalRequest.objects.filter(
            requesting_user__id=logged_in_user_profile.id,
            request_type=Requests.get('REQUEST_PAYMENT')
        ).order_by('-updated_at').all())()
        paginated_response = await sync_to_async(get_paginated_bulk_response)(request, queryset)
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
            request_type=Requests.get('REQUEST_PAYMENT'),
            amount_value__gte=approve_threshold,
            created_at__gte=logged_in_user.date_joined
        ).order_by('-updated_at').all())()

        if get_pending:
            queryset = await sync_to_async(lambda: [req for req in base_queryset if not req.rejected_by.exists() and logged_in_user not in req.approved_by.all()])()
        else:
            queryset = base_queryset
        paginated_response = await sync_to_async(get_paginated_bulk_response)(request, queryset)
        return JsonResponse(paginated_response)

@async_permission_required('auth.my_payment_requests', raise_exception=True)
@api_view(['GET'])
async def payment_my_requests(request):
    logged_in_user_profile=await sync_to_async(get_logged_in_user_profile_instance)(request)
    

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

@async_permission_required('auth.bulk_contract_request', raise_exception=True)
@api_view(['POST'])
async def bulk_contract_import_request(request):
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

    instance = ApprovalRequest(
        requesting_user=logged_in_user_profile,
        request_type=Requests.get('CONTRACT_BULK_IMPORT'), 
        file=uploaded_file, 
        remark=request.POST.get('remark'), 
    )
    await sync_to_async(instance.save)()

    approver_group = await sync_to_async(Group.objects.get)(name='Approver')
    approvers = await sync_to_async(User.objects.filter)(groups=approver_group)
    approvers_user_ids = await sync_to_async(lambda: [user.id for user in approvers])()
    approver_user_profiles = await sync_to_async(lambda: UserProfile.objects.filter(
        user__id__in=approvers_user_ids,
        user__userprofile__api_key=logged_in_user_profile.api_key
    ))()
    approver_objects = await sync_to_async(lambda: [approver_user_profile.user for approver_user_profile in approver_user_profiles])()
    approvers_count = await sync_to_async(approver_user_profiles.count)()

    await sync_to_async(add_approver_sync)(instance, approver_objects)

    if approvers_count == 0:
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
        import_contract_rows.delay(data, saved_id, logged_in_user_profile.api_key.api_key)

        return JsonResponse({"message": "Contracts Import in Progress!!"}, safe=False)

    return JsonResponse({"message": "Contracts Import Request created!!"}, safe=False)

@async_permission_required('auth.approval_bulk_contract_import', raise_exception=True)
@api_view(['POST'])
async def submit_bulk_contract_response(request):
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

        approver_group = await sync_to_async(Group.objects.get)(name='Approver')
        approvers = await sync_to_async(User.objects.filter)(groups=approver_group)
        approvers_user_ids = await sync_to_async(lambda: [user.id for user in approvers])()
        approvers_count = await sync_to_async(lambda: UserProfile.objects.filter(
            user__id__in=approvers_user_ids,
            user__userprofile__api_key=approval_request.requesting_user.api_key
        ).count())()

        approved_users = await sync_to_async(approval_request.approved_by.all)()
        approved_users_count = await sync_to_async(approved_users.count)()

        if approvers_count == approved_users_count:
            instance = ImportedDocuments(
                file_name=file_name, 
                remark=remark, 
                import_type=ImportTypes.get('CONTRACT'), 
                failed_count=0, 
                successful_count=0, 
                on_queue_count=len(data),
                user_id=logged_in_user
            )
            await sync_to_async(instance.save)()
            saved_id = instance.uuid
            import_contract_rows.delay(data, saved_id, logged_in_user_profile.api_key)

            return JsonResponse({"message": "Contracts Import in Progress!!"}, safe=False)
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


@async_permission_required('auth.bulk_contract_requests', raise_exception=True)
@api_view(['GET'])
async def contract_bulk_requests(request):
    logged_in_user=await sync_to_async(get_logged_in_user)(request)
    logged_in_user_profile=await sync_to_async(get_logged_in_user_profile_instance)(request)

    approver_group = await sync_to_async(Group.objects.get)(name='Approver')
    is_approver = await sync_to_async(lambda: logged_in_user.groups.filter(id=approver_group.id).exists())()

    if not is_approver:
        queryset = await sync_to_async(lambda: ApprovalRequest.objects.filter(
            requesting_user__id=logged_in_user_profile.id,
            request_type=Requests.get('CONTRACT_BULK_IMPORT')
        ).order_by('-updated_at').all())()
        paginated_response = await sync_to_async(get_paginated_response)(request, queryset)
        return JsonResponse(paginated_response)  
    else:
        queryset = await sync_to_async(lambda: ApprovalRequest.objects.filter(
            requesting_user__api_key=logged_in_user_profile.api_key,
            request_type=Requests.get('CONTRACT_BULK_IMPORT')
        ).order_by('-updated_at').all())()
        paginated_response = await sync_to_async(get_paginated_response)(request, queryset)
        return JsonResponse(paginated_response)

@async_permission_required('auth.bulk_payment_request', raise_exception=True)
@api_view(['POST'])
async def bulk_import_payment_request(request):
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

    instance = ApprovalRequest(
        requesting_user=logged_in_user_profile,
        request_type=Requests.get('REQUEST_PAYMENT_BULK_IMPORT'), 
        file=uploaded_file, 
        remark=request.POST.get('remark'), 
    )
    await sync_to_async(instance.save)()

    approver_group = await sync_to_async(Group.objects.get)(name='Approver')
    approvers = await sync_to_async(User.objects.filter)(groups=approver_group)
    approvers_user_ids = await sync_to_async(lambda: [user.id for user in approvers])()
    approver_user_profiles = await sync_to_async(lambda: UserProfile.objects.filter(
        user__id__in=approvers_user_ids,
        user__userprofile__api_key=logged_in_user_profile.api_key
    ))()
    approver_objects = await sync_to_async(lambda: [approver_user_profile.user for approver_user_profile in approver_user_profiles])()
    approvers_count = await sync_to_async(approver_user_profiles.count)()

    await sync_to_async(add_approver_sync)(instance, approver_objects)

    if approvers_count == 0:
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
        import_recurring_payment_request_rows.delay(data, saved_id, logged_in_user_profile.api_key.api_key)

        return JsonResponse({"message": "Payment Requests Import in Progress!!"}, safe=False)

    return JsonResponse({"message": "Payment Requests Import Request created!!"}, safe=False)

@async_permission_required('auth.approval_bulk_payment_request_import', raise_exception=True)
@api_view(['POST'])
async def submit_bulk_payment_request_response(request):
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

        approver_group = await sync_to_async(Group.objects.get)(name='Approver')
        approvers = await sync_to_async(User.objects.filter)(groups=approver_group)
        approvers_user_ids = await sync_to_async(lambda: [user.id for user in approvers])()
        approvers_count = await sync_to_async(lambda: UserProfile.objects.filter(
            user__id__in=approvers_user_ids,
            user__userprofile__api_key=approval_request.requesting_user.api_key
        ).count())()

        approved_users = await sync_to_async(approval_request.approved_by.all)()
        approved_users_count = await sync_to_async(approved_users.count)()

        if approvers_count == approved_users_count:
            instance = ImportedDocuments(
                file_name=file_name, 
                remark=remark, 
                import_type=ImportTypes.get('REQUEST_PAYMENT'), 
                failed_count=0, 
                successful_count=0, 
                on_queue_count=len(data),
                user_id=logged_in_user
            )
            await sync_to_async(instance.save)()
            saved_id = instance.uuid
            import_recurring_payment_request_rows.delay(data, saved_id, logged_in_user_profile.api_key)

            return JsonResponse({"message": "Request Payment Import in Progress!!"}, safe=False)
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

@async_permission_required('auth.bulk_requested_payments', raise_exception=True)
@api_view(['GET'])
async def request_payment_bulk_requests(request):
    logged_in_user=await sync_to_async(get_logged_in_user)(request)
    logged_in_user_profile=await sync_to_async(get_logged_in_user_profile_instance)(request)

    approver_group = await sync_to_async(Group.objects.get)(name='Approver')
    is_approver = await sync_to_async(lambda: logged_in_user.groups.filter(id=approver_group.id).exists())()

    if not is_approver:
        queryset = await sync_to_async(lambda: ApprovalRequest.objects.filter(
            requesting_user__id=logged_in_user_profile.id,
            request_type=Requests.get('REQUEST_PAYMENT_BULK_IMPORT')
        ).order_by('-updated_at').all())()
        paginated_response = await sync_to_async(get_paginated_response)(request, queryset)
        return JsonResponse(paginated_response)
    else:
        queryset = await sync_to_async(lambda: ApprovalRequest.objects.filter(
            requesting_user__api_key=logged_in_user_profile.api_key,
            request_type=Requests.get('REQUEST_PAYMENT_BULK_IMPORT')
        ).order_by('-updated_at').all())()
        paginated_response = await sync_to_async(get_paginated_response)(request, queryset)
        return JsonResponse(paginated_response)