import jwt
import json
from ..models import User, UserProfile
from django.db.models import Q, Count
from django.contrib.auth.models import Group
from django.core.paginator import Paginator
from django.utils import timezone
from ..serializers.serializers import ApprovalRequestSerializer, UserProfileExtendedSerializer
from django.core.files.storage import default_storage
import requests
import pandas as pd
from io import BytesIO
import os

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
  user_profile_dict = UserProfileExtendedSerializer(logged_in_user_profile)
  return user_profile_dict.data

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

def get_paginated_response(request, queryset):
  per_page = request.GET.get('perPage', 15)
  paginator = Paginator(queryset, per_page)
    
  page_number = request.GET.get('page', 1)
  page_obj = paginator.get_page(page_number)

  serializer = ApprovalRequestSerializer(page_obj.object_list, many=True)
  data = serializer.data

  return {
      'data': data,
      'page': page_obj.number,
      'lastPage': paginator.num_pages,
      'total': paginator.count,
      'perPage': per_page
  }

def get_file_content(file_url):
    file_path = file_url.lstrip('/')

    with default_storage.open(file_path, 'r') as file:
        content = file.read()

    return content

def download_file(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.content

def read_file(file_content, url):
    with BytesIO(file_content) as f:
        if url.endswith(('xlsx')):
            df = pd.read_excel(f, engine='openpyxl')
        elif url.endswith(('xls')):
            df = pd.read_excel(f, engine='xlrd')
        elif url.endswith(('csv')):
            df = pd.read_csv(f)
        else:
            raise ValueError("Unsupported file type")
    return df

def convert_to_json(df):
    return df.to_json(orient='records')

def process_file(url):
    if not url.startswith('http://') and not url.startswith('https://'):
        url = os.environ.get('YAYA_BASE_URL') + url
    file_content = download_file(url)
    df = read_file(file_content, url)
    json_data = convert_to_json(df)
    return json_data

def get_paginated_bulk_response(request, queryset):
  per_page = request.GET.get('perPage', 15)
  paginator = Paginator(queryset, per_page)
    
  page_number = request.GET.get('page', 1)
  page_obj = paginator.get_page(page_number)

  serializer = ApprovalRequestSerializer(page_obj.object_list, many=True)
  datas = serializer.data
  updated_datas = [{**data, 'file': json.loads(process_file(data['file']))} for data in datas]

  return {
      'data': updated_datas,
      'page': page_obj.number,
      'lastPage': paginator.num_pages,
      'total': paginator.count,
      'perPage': per_page
  }

def add_approver_sync(instance, approver_objects): 
  instance.approvers.add(*approver_objects)
  instance.save()

def get_approver_objects(user, approval_request, amount = None): 
  approver_group = Group.objects.get(name='Approver')
  approvers = User.objects.filter(groups=approver_group)
  approvers_user_ids = [user.id for user in approvers]
  if approval_request.created_at :
    request_time = approval_request.created_at 
  else:
    request_time = timezone.now()
  approver_user_profiles = UserProfile.objects.filter(
      user__id__in=approvers_user_ids,
      user__userprofile__api_key=user.api_key,
      user__date_joined__lte=request_time
  ).annotate(
      approverrule_count=Count('approverrule')
  ).filter(
      Q(approverrule__approve_threshold__lt=amount) | Q(approverrule_count=0) if amount is not None else Q(approverrule_count__gte=0)
  )
  return [approver_user_profile.user for approver_user_profile in approver_user_profiles]