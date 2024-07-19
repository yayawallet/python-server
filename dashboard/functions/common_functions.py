import jwt
import json
from ..models import User

def get_logged_in_user(request):
  auth_header = request.headers.get('Authorization')
  token = auth_header.split(' ')[1]
  decoded_token = jwt.decode(jwt=token, algorithms=["HS256"], options={'verify_signature':False})
  logged_in_user = User.objects.get(id=decoded_token.get("user_id"))
  return logged_in_user

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