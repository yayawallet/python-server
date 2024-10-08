from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        token['user_id'] = user.id
        token['username'] = user.username
        token['roles'] = list(user.groups.values_list('name', flat=True))
        
        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        data['user'] = {
            'user_id': self.user.id,
            'username': self.user.username,
            'api_key': self.user.userprofile.api_key.api_key,
            'roles': list(self.user.groups.values_list('name', flat=True)),
            'permissions': list(self.user.get_group_permissions())
        }

        return data