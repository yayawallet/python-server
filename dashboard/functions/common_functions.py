import jwt
import json
from ..models import User, UserProfile

def get_logged_in_user(request):
  auth_header = request.headers.get('Authorization')
  token = auth_header.split(' ')[1]
  decoded_token = jwt.decode(jwt=token, algorithms=["HS256"], options={'verify_signature':False})
  logged_in_user = User.objects.get(id=decoded_token.get("user_id"))
  return logged_in_user

def get_logged_in_user_profile(request):
  auth_header = request.headers.get('Authorization')
  token = auth_header.split(' ')[1]
  decoded_token = jwt.decode(jwt=token, algorithms=["HS256"], options={'verify_signature':False})
  logged_in_user_profile = UserProfile.objects.get(user_id=decoded_token.get("user_id"))
  return logged_in_user_profile.api_key

def get_logged_in_user_profile_object(request):
  auth_header = request.headers.get('Authorization')
  token = auth_header.split(' ')[1]
  decoded_token = jwt.decode(jwt=token, algorithms=["HS256"], options={'verify_signature':False})
  logged_in_user_profile = UserProfile.objects.get(user_id=decoded_token.get("user_id"))
  user_profile_dict = {
        'user_id': logged_in_user_profile.user.id,
        'country': logged_in_user_profile.country,
        'address': logged_in_user_profile.address,
        'region': logged_in_user_profile.region,
        'phone': logged_in_user_profile.phone,
        'date_of_birth': logged_in_user_profile.date_of_birth.isoformat() if logged_in_user_profile.date_of_birth else None,
        'profile_image': logged_in_user_profile.profile_image.url if logged_in_user_profile.profile_image else None,
        'id_image': logged_in_user_profile.id_image.url if logged_in_user_profile.id_image else None,
    }
  return user_profile_dict

def get_logged_in_user_profile_instance(request):
  auth_header = request.headers.get('Authorization')
  token = auth_header.split(' ')[1]
  decoded_token = jwt.decode(jwt=token, algorithms=["HS256"], options={'verify_signature':False})
  logged_in_user_profile = UserProfile.objects.get(user_id=decoded_token.get("user_id"))
  return logged_in_user_profile

def parse_response(response):
  content = ''
  for chunk in response.streaming_content:
      if chunk:
          content += chunk.decode('utf-8')

  try:
      parsed_data = json.loads(content)
  except json.JSONDecodeError as e:
      print(f"Error parsing JSON: {e}")
      parsed_data = None

  return parsed_data

def get_dict_by_property_value(data, property_name, value):
    for item in data:
        if item.get(property_name) == value:
            return item
    return None