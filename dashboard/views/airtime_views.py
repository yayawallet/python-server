from adrf.decorators import api_view
from rest_framework.response import Response
from ..permisssions.async_permission import async_permission_required
from yayawallet_python_sdk.api import airtime
from .stream_response import stream_response
from ..functions.common_functions import get_logged_in_user, parse_response, get_logged_in_user_profile, get_logged_in_user_profile_instance, get_paginated_response
from ..models import ActionTrail, ApprovalRequest, UserProfile, RejectedRequest
from asgiref.sync import sync_to_async
from ..constants import Actions, Requests, Approve
from django.http.response import JsonResponse
from django.contrib.auth.models import User, Group
from ..serializers.serializers import ApprovalRequestSerializer
from django.db.models import Q
import json
import jwt

@async_permission_required('auth.airtime_request', raise_exception=True)
@api_view(['POST'])
async def airtime_request(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    logged_in_user_profile=await sync_to_async(get_logged_in_user_profile_instance)(request)
    data = request.data

    instance = ApprovalRequest(
        request_json=json.dumps(data),
        requesting_user=logged_in_user_profile,
        request_type=Requests.get('AIRTIME'), 
    )

    approver_group = await sync_to_async(Group.objects.get)(name='Approver')
    approvers = await sync_to_async(User.objects.filter)(groups=approver_group)
    approvers_user_ids = await sync_to_async(lambda: [user.id for user in approvers])()
    approvers_count = await sync_to_async(lambda: UserProfile.objects.filter(
        user__id__in=approvers_user_ids,
        user__userprofile__api_key=logged_in_user_profile.api_key
    ).count())()

    await sync_to_async(instance.approvers.add)(*approvers)
    await sync_to_async(instance.save)()

    if approvers_count == 0:
        response = await airtime.buy_airtime(
            data.get('phone'), 
            data.get('amount'),
            logged_in_user.api_key
            )
        
        if response.status_code == 200 or response.status_code == 201:
            parsed_data = parse_response(response)
            
            instance = ActionTrail(
                user_id=await sync_to_async(get_logged_in_user)(request), 
                action_id=parsed_data.get('id'), 
                action_type=Actions.get("AIRTIME")
            )
            await sync_to_async(instance.save)()
            return JsonResponse(parsed_data, safe=False)
            
        return stream_response(response)

    return JsonResponse({"message": "Airtime Request created!!"}, safe=False)

@async_permission_required('auth.approval_airtime', raise_exception=True)
@api_view(['POST'])
async def submit_airtime_response(request):
    auth_header = request.headers.get('Authorization')
    token = auth_header.split(' ')[1]
    decoded_token = jwt.decode(jwt=token, algorithms=["HS256"], options={'verify_signature':False})
    logged_in_user = await sync_to_async(User.objects.get)(id=decoded_token.get("user_id"))
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
            response = await airtime.buy_airtime(
                data.get('phone'), 
                data.get('amount'),
                logged_in_user.api_key
                )
            
            if response.status_code == 200 or response.status_code == 201:
                parsed_data = parse_response(response)
                
                instance = ActionTrail(
                    user_id=approval_request.requesting_user, 
                    action_id=parsed_data.get('id'), 
                    action_type=Actions.get("AIRTIME")
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

@async_permission_required('auth.airtime_requests', raise_exception=True)
@api_view(['GET'])
async def airtime_requests(request):
    logged_in_user=await sync_to_async(get_logged_in_user)(request)
    logged_in_user_profile=await sync_to_async(get_logged_in_user_profile_instance)(request)
    queryset = await sync_to_async(lambda: ApprovalRequest.objects.filter(
        requesting_user__api_key=logged_in_user_profile.api_key,
        request_type=Requests.get('AIRTIME')
    ).exclude(
        Q(approved_by=logged_in_user) | Q(rejected_by__user=logged_in_user)
    ).all())()
    paginated_response = await sync_to_async(get_paginated_response)(request, queryset)
    return JsonResponse(paginated_response)


@async_permission_required('auth.my_airtime_requests', raise_exception=True)
@api_view(['GET'])
async def airtime_my_requests(request):
    logged_in_user_profile=await sync_to_async(get_logged_in_user_profile_instance)(request)
    queryset = await sync_to_async(lambda: ApprovalRequest.objects.filter(
        requesting_user__id=logged_in_user_profile.id,
        request_type=Requests.get('AIRTIME')
    ).all())()
    paginated_response = await sync_to_async(get_paginated_response)(request, queryset)
    return JsonResponse(paginated_response)

@async_permission_required('auth.package_request', raise_exception=True)
@api_view(['POST'])
async def package_request(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    logged_in_user_profile=await sync_to_async(get_logged_in_user_profile_instance)(request)
    data = request.data

    instance = ApprovalRequest(
        request_json=json.dumps(data),
        requesting_user=logged_in_user_profile,
        request_type=Requests.get('PACKAGE'), 
    )

    approver_group = await sync_to_async(Group.objects.get)(name='Approver')
    approvers = await sync_to_async(User.objects.filter)(groups=approver_group)
    approvers_user_ids = await sync_to_async(lambda: [user.id for user in approvers])()
    approvers_count = await sync_to_async(lambda: UserProfile.objects.filter(
        user__id__in=approvers_user_ids,
        user__userprofile__api_key=logged_in_user_profile.api_key
    ).count())()

    await sync_to_async(instance.approvers.add)(*approvers)
    await sync_to_async(instance.save)()

    if approvers_count == 0:
        response = await airtime.buy_package(
            data.get('phone'), 
            data.get('package'),
            logged_in_user.api_key
            )
        
        if response.status_code == 200 or response.status_code == 201:
            parsed_data = parse_response(response)
            
            instance = ActionTrail(
                user_id=await sync_to_async(get_logged_in_user)(request), 
                action_id=parsed_data.get('id'), 
                action_type=Actions.get("PACKAGE")
            )
            await sync_to_async(instance.save)()
            return JsonResponse(parsed_data, safe=False)
            
        return stream_response(response)

    return JsonResponse({"message": "Package Request created!!"}, safe=False)

@async_permission_required('auth.approval_package', raise_exception=True)
@api_view(['POST'])
async def submit_package_response(request):
    auth_header = request.headers.get('Authorization')
    token = auth_header.split(' ')[1]
    decoded_token = jwt.decode(jwt=token, algorithms=["HS256"], options={'verify_signature':False})
    logged_in_user = await sync_to_async(User.objects.get)(id=decoded_token.get("user_id"))
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
            response = await airtime.buy_package(
                data.get('phone'), 
                data.get('package'),
                logged_in_user.api_key
                )
            
            if response.status_code == 200 or response.status_code == 201:
                parsed_data = parse_response(response)
                
                instance = ActionTrail(
                    user_id=approval_request.requesting_user, 
                    action_id=parsed_data.get('id'), 
                    action_type=Actions.get("PACKAGE")
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

@async_permission_required('auth.package_requests', raise_exception=True)
@api_view(['GET'])
async def package_requests(request):
    logged_in_user=await sync_to_async(get_logged_in_user)(request)
    logged_in_user_profile=await sync_to_async(get_logged_in_user_profile_instance)(request)
    queryset = await sync_to_async(lambda: ApprovalRequest.objects.filter(
        requesting_user__api_key=logged_in_user_profile.api_key,
        request_type=Requests.get('PACKAGE')
    ).exclude(
        Q(approved_by=logged_in_user) | Q(rejected_by__user=logged_in_user)
    ).all())()
    paginated_response = await sync_to_async(get_paginated_response)(request, queryset)
    return JsonResponse(paginated_response)


@async_permission_required('auth.my_package_requests', raise_exception=True)
@api_view(['GET'])
async def package_my_requests(request):
    logged_in_user_profile=await sync_to_async(get_logged_in_user_profile_instance)(request)
    queryset = await sync_to_async(lambda: ApprovalRequest.objects.filter(
        requesting_user__id=logged_in_user_profile.id,
        request_type=Requests.get('PACKAGE')
    ).all())()
    paginated_response = await sync_to_async(get_paginated_response)(request, queryset)
    return JsonResponse(paginated_response)

@api_view(['GET'])
async def proxy_list_recharges(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    response = await airtime.list_recharges(logged_in_user.api_key)
    return stream_response(response)

@api_view(['POST'])
async def proxy_list_packages(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    data = request.data
    response = await airtime.list_packages(
        data.get('phone'),
        logged_in_user.api_key
        )
    return stream_response(response)