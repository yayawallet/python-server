from functools import wraps
from django.core.exceptions import PermissionDenied
import jwt
from django.utils.decorators import sync_and_async_middleware
from django.http.response import JsonResponse
from ..models import User
from asgiref.sync import sync_to_async

def async_permission_required(perm, raise_exception=False):
    def decorator(view_func):
        @wraps(view_func)
        async def _wrapped_view(request, *args, **kwargs):
            auth_header = request.headers.get('Authorization')
            token = auth_header.split(' ')[1]
            decoded_token = jwt.decode(jwt=token, algorithms=["HS256"], options={'verify_signature':False})
            user = await sync_to_async(User.objects.get)(id=decoded_token.get("user_id"))
            user_permissions = await sync_to_async(user.get_group_permissions)()
            if perm in list(user_permissions):
                return await view_func(request, *args, **kwargs)
            else:
                return JsonResponse({"message": "You don't have the required permission!!", "permission": perm}, safe=False, status=403)
        return sync_and_async_middleware(_wrapped_view)
    return decorator