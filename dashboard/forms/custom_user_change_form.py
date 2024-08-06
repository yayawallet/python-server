from django import forms
from django.contrib.auth.models import User

class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'groups', 'is_active', 'is_staff', 'is_superuser', 'user_permissions')
        # Note: Exclude 'user_permissions' field