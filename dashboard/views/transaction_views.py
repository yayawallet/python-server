from adrf.decorators import api_view
from ..permisssions.async_permission import async_permission_required
from yayawallet_python_sdk.api import transaction
from .stream_response import stream_response
from ..models import ActionTrail, ApprovalRequest, UserProfile, RejectedRequest
from asgiref.sync import sync_to_async
from ..functions.common_functions import get_logged_in_user, parse_response, get_logged_in_user_profile, get_logged_in_user_profile_instance, get_paginated_response, add_approver_sync
from django.http.response import JsonResponse
from rest_framework.response import Response
from ..constants import Actions, Requests, Approve
import json
import jwt
from django.db.models import Q
from django.contrib.auth.models import User, Group
from ..serializers.serializers import ApprovalRequestSerializer

@api_view(['GET'])
async def proxy_get_transaction_list_by_user(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    page = request.GET.get('p')
    if not page:
        page = "1"
    params = "?p=" + page
    response = await transaction.get_transaction_list_by_user(params, logged_in_user.api_key)
    return stream_response(response)

@async_permission_required('auth.transaction_request', raise_exception=True)
@api_view(['POST'])
async def transaction_request(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    logged_in_user_profile=await sync_to_async(get_logged_in_user_profile_instance)(request)
    data = request.data

    instance = ApprovalRequest(
        request_json=json.dumps(data),
        requesting_user=logged_in_user_profile,
        request_type=Requests.get('TRANSACTION'), 
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
        response = await transaction.create_transaction(
            data.get('receiver'), 
            data.get('amount'),
            data.get('cause'),
            data.get('meta_data'),
            logged_in_user.api_key
            )
        
        if response.status_code == 200 or response.status_code == 201:
            parsed_data = parse_response(response)
            
            instance = ActionTrail(
                user_id=await sync_to_async(get_logged_in_user)(request), 
                action_id=parsed_data.get('id'), 
                action_type=Actions.get("TRANSACTION")
            )
            await sync_to_async(instance.save)()
            return JsonResponse(parsed_data, safe=False)
            
        return stream_response(response)

    return JsonResponse({"message": "Transaction Request created!!"}, safe=False)

@async_permission_required('auth.approval_transaction', raise_exception=True)
@api_view(['POST'])
async def submit_transaction_response(request):
    auth_header = request.headers.get('Authorization')
    token = auth_header.split(' ')[1]
    decoded_token = jwt.decode(jwt=token, algorithms=["HS256"], options={'verify_signature':False})
    logged_in_user = await sync_to_async(User.objects.get)(id=decoded_token.get("user_id"))
    logged_in_user_profile = await sync_to_async(get_logged_in_user_profile)(request)
    approval_request = await sync_to_async(ApprovalRequest.objects.get)(uuid=request.POST.get('approval_request_id'))
    
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
            response = await transaction.create_transaction(
                data.get('receiver'), 
                data.get('amount'),
                data.get('cause'),
                meta_data,
                logged_in_user_profile.api_key
                )
            
            if response.status_code == 200 or response.status_code == 201:
                parsed_data = parse_response(response)
                requesting_user_object = await sync_to_async(lambda: approval_request.requesting_user.user)()
                
                instance = ActionTrail(
                    user_id=requesting_user_object, 
                    action_id=parsed_data.get('id'), 
                    action_type=Actions.get("TRANSACTION")
                )
                await sync_to_async(instance.save)()
                return JsonResponse(parsed_data, safe=False)
                
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

@async_permission_required('auth.transaction_requests', raise_exception=True)
@api_view(['GET'])
async def transaction_requests(request):
    logged_in_user=await sync_to_async(get_logged_in_user)(request)
    logged_in_user_profile=await sync_to_async(get_logged_in_user_profile_instance)(request)

    approver_group = await sync_to_async(Group.objects.get)(name='Approver')
    is_approver = await sync_to_async(lambda: logged_in_user.groups.filter(id=approver_group.id).exists())()

    if not is_approver:
        queryset = await sync_to_async(lambda: ApprovalRequest.objects.filter(
            requesting_user__id=logged_in_user_profile.id,
            request_type=Requests.get('TRANSACTION')
        ).all())()
        paginated_response = await sync_to_async(get_paginated_response)(request, queryset)
        return JsonResponse(paginated_response)
    else:
        queryset = await sync_to_async(lambda: ApprovalRequest.objects.filter(
            requesting_user__api_key=logged_in_user_profile.api_key,
            request_type=Requests.get('TRANSACTION')
        ).all())()
        paginated_response = await sync_to_async(get_paginated_response)(request, queryset)
        return JsonResponse(paginated_response)

@api_view(['POST'])
async def proxy_transaction_fee(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    data = request.data
    response = await transaction.transaction_fee(
        data.get('receiver'), 
        data.get('amount'),
        logged_in_user.api_key
        )
    return stream_response(response)

@async_permission_required('auth.generate_qr_url', raise_exception=True)
@api_view(['POST'])
async def proxy_generate_qr_url(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    data = request.data
    response = await transaction.generate_qr_url(
        data.get('amount'), 
        data.get('cause'),
        logged_in_user.api_key
        )
    return stream_response(response)

@api_view(['GET'])
async def proxy_get_transaction_by_id(request, id):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    response = await transaction.get_transaction_by_id(id, logged_in_user.api_key)
    return stream_response(response)

@api_view(['POST'])
async def proxy_search_transaction(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    data = request.data
    response = await transaction.search_transaction(
        data.get('query'),
        logged_in_user.api_key
        )
    return stream_response(response)