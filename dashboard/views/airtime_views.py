from adrf.decorators import api_view
from rest_framework.response import Response
from ..permisssions.async_permission import async_permission_required
from yayawallet_python_sdk.api import airtime
from .stream_response import stream_response
from ..functions.common_functions import get_logged_in_user, parse_response, get_logged_in_user_profile, get_logged_in_user_profile_instance, get_paginated_response, add_approver_sync, get_approver_objects
from ..models import ActionTrail, ApprovalRequest, UserProfile, RejectedRequest, ApproverRule
from asgiref.sync import sync_to_async
from ..constants import Actions, Requests, Approve, Pending
from django.http.response import JsonResponse
from django.contrib.auth.models import User, Group
from ..serializers.serializers import ApprovalRequestSerializer
from django.db.models import Q
import jwt
from django.db.models.functions import Cast
from django.db.models.fields import IntegerField
from django.db.models.fields.json import KeyTextTransform
from django.core.exceptions import ObjectDoesNotExist

@async_permission_required('auth.airtime_request', raise_exception=True)
@api_view(['POST'])
async def airtime_request(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    logged_in_user_profile=await sync_to_async(get_logged_in_user_profile_instance)(request)
    
    data = request.data
    amount = data.get("amount")

    approval_request = ApprovalRequest(
        request_json=data,
        requesting_user=logged_in_user_profile,
        request_type=Requests.get('AIRTIME'), 
    )

    approver_objects = await sync_to_async(get_approver_objects)(logged_in_user_profile, amount, approval_request)
    approvers_count = len(approver_objects)

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
            approval_request.is_successful = True
            await sync_to_async(approval_request.save)()
            return JsonResponse(parsed_data, safe=False)
        
        approval_request.is_successful = False
        await sync_to_async(approval_request.save)()  
        return stream_response(response)
        
    await sync_to_async(approval_request.save)()

    await sync_to_async(add_approver_sync)(approval_request, approver_objects)

    return JsonResponse({"message": "Airtime Request created!!"}, safe=False)

@async_permission_required('auth.approval_airtime', raise_exception=True)
@api_view(['POST'])
async def submit_airtime_response(request):
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

        approver_objects = await sync_to_async(get_approver_objects)(requester, amount, approval_request)
        approvers_count = len(approver_objects)
        approved_users = await sync_to_async(approval_request.approved_by.all)()
        approved_users_count = await sync_to_async(approved_users.count)()

        if approvers_count == approved_users_count:
            data = approval_request.request_json
            if approval_request.request_type == Requests.get('AIRTIME'):
                response = await airtime.buy_airtime(
                    data.get('phone'), 
                    data.get('amount'),
                    logged_in_user_profile.api_key
                    )
                
                if response.status_code == 200 or response.status_code == 201:
                    parsed_data = parse_response(response)
                    requesting_user_object = await sync_to_async(lambda: approval_request.requesting_user.user)()
                    
                    instance = ActionTrail(
                        user_id=requesting_user_object, 
                        action_id=parsed_data.get('id'), 
                        action_type=Actions.get("AIRTIME")
                    )
                    await sync_to_async(instance.save)()
                    approval_request.is_successful = True
                    await sync_to_async(approval_request.save)()
                    return JsonResponse(parsed_data, safe=False)
            
                approval_request.is_successful = False
                await sync_to_async(approval_request.save)()
                return stream_response(response)
            
            elif approval_request.request_type == Requests.get('PACKAGE'):
                response = await airtime.buy_package(
                    data.get('phone'), 
                    data.get('package'),
                    logged_in_user_profile.api_key
                    )
                
                if response.status_code == 200 or response.status_code == 201:
                    parsed_data = parse_response(response)
                    requesting_user_object = await sync_to_async(lambda: approval_request.requesting_user.user)()
                    
                    instance = ActionTrail(
                        user_id=requesting_user_object, 
                        action_id=parsed_data.get('id'), 
                        action_type=Actions.get("PACKAGE")
                    )
                    await sync_to_async(instance.save)()
                    approval_request.is_successful = True
                    await sync_to_async(approval_request.save)()
                    return JsonResponse(parsed_data, safe=False)
                
                approval_request.is_successful = False
                await sync_to_async(approval_request.save)()
                return stream_response(response)
            else:
                JsonResponse({"message": "Request type not recognized!!"}, safe=False)
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
    
    approver_group = await sync_to_async(Group.objects.get)(name='Approver')
    is_approver = await sync_to_async(lambda: logged_in_user.groups.filter(id=approver_group.id).exists())()

    if not is_approver:
        queryset = await sync_to_async(lambda: ApprovalRequest.objects.filter(
            Q(request_type=Requests.get('AIRTIME')) | Q(request_type=Requests.get('PACKAGE')),
            requesting_user__id=logged_in_user_profile.id,
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
            Q(request_type=Requests.get('AIRTIME')) | Q(request_type=Requests.get('PACKAGE')),
            requesting_user__api_key=logged_in_user_profile.api_key,
            amount_value__gte=approve_threshold,
            created_at__gte=logged_in_user.date_joined
        ).all())()
        if get_pending:
            queryset = await sync_to_async(lambda: [req for req in base_queryset if not req.rejected_by.exists() and logged_in_user not in req.approved_by.all()])()
        else:
            queryset = base_queryset
        paginated_response = await sync_to_async(get_paginated_response)(request, queryset)
        return JsonResponse(paginated_response) 

@async_permission_required('auth.package_request', raise_exception=True)
@api_view(['POST'])
async def package_request(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile)(request)
    logged_in_user_profile=await sync_to_async(get_logged_in_user_profile_instance)(request)
    
    data = request.data
    amount = data.get("amount")

    approval_request = ApprovalRequest(
        request_json=data,
        requesting_user=logged_in_user_profile,
        request_type=Requests.get('PACKAGE'), 
    )

    approver_objects = await sync_to_async(get_approver_objects)(logged_in_user_profile, amount, approval_request)
    approvers_count = len(approver_objects)

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
            approval_request.is_successful = True
            await sync_to_async(approval_request.save)()
            return JsonResponse(parsed_data, safe=False)
        
        approval_request.is_successful = False
        await sync_to_async(approval_request.save)() 
        return stream_response(response)

    await sync_to_async(approval_request.save)()

    await sync_to_async(add_approver_sync)(approval_request, approver_objects)

    return JsonResponse({"message": "Package Request created!!"}, safe=False)

def get_approval_request_serialized_data(db_results):
    serializer = ApprovalRequestSerializer(db_results, many=True)
    return serializer.data

def get_single_approval_request_serialized_data(db_results):
    serializer = ApprovalRequestSerializer(db_results)
    return serializer.data    

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