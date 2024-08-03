# admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile
import os

class UserProfileStaffInline(admin.StackedInline):
    model = UserProfile
    can_delete = False

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    fields = ('country', 'address', 'region', 'phone', 'date_of_birth', 'profile_image', 'id_image')  # Exclude 'api_key'
    
class AccountsUserAdmin(AuthUserAdmin):
    def save_model(self, request, obj, form, change):
        if not change:
            user = super().save_model(request, obj, form, change)
            admin_profile = request.user.userprofile
            instance = UserProfile.objects.get(user=obj)
            instance.api_key = admin_profile.api_key
            instance.save()
        else:
            super().save_model(request, obj, form, change)

    def add_view(self, *args, **kwargs):
        self.inlines = []
        return super(AccountsUserAdmin, self).add_view(*args, **kwargs)
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        user = request.user
        if user.username == os.environ.get('DJANGO_SUPERUSER_USERNAME') and user.check_password(os.environ.get('DJANGO_SUPERUSER_PASSWORD')):
            self.inlines = [UserProfileStaffInline]
        else:
            self.inlines = [UserProfileInline]
        
        return super(AccountsUserAdmin, self).change_view(request, object_id, form_url, extra_context)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user
        if user.username == os.environ.get('DJANGO_SUPERUSER_USERNAME') and user.check_password(os.environ.get('DJANGO_SUPERUSER_PASSWORD')):
            return qs
        api_key = user.userprofile.api_key

        if api_key:
            return qs.filter(userprofile__api_key=api_key).exclude(username=os.environ.get('DJANGO_SUPERUSER_USERNAME'))
        else:
            return qs.none()

admin.site.unregister(User)
admin.site.register(User, AccountsUserAdmin)
