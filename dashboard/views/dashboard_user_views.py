from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from ..serializers.user_serializers import ChangePasswordSerializer
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
from adrf.decorators import api_view
from ..functions.common_functions import get_logged_in_user
from django.http.response import JsonResponse
from ..models import UserProfile
from asgiref.sync import sync_to_async
from ..functions.common_functions import get_logged_in_user_profile_object
from ..serializers.serializers import UserProfileSerializer

@api_view(['POST'])
async def proxy_change_password(request):
    old_password = request.data.get("old_password")
    new_password = request.data.get("new_password")

    user = request.user

    if not user.check_password(old_password):
      return JsonResponse({"message": "Old password is not correct"}, safe=False, status=400)
    
    user.set_password(new_password)
    await sync_to_async(user.save)()

    return JsonResponse({"message": "Password successfully changed!"}, safe=False)

@api_view(['GET'])
async def proxy_get_dashboard_user(request):
    logged_in_user=await sync_to_async(get_logged_in_user_profile_object)(request)
    return JsonResponse(logged_in_user, safe=False)

