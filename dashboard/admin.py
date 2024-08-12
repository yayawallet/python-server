# admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, ApiKey, ActionTrail
import os
from .forms.custom_user_change_form import CustomUserChangeForm

class UserProfileStaffInline(admin.StackedInline):
    model = UserProfile
    can_delete = False

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    fields = ('country', 'address', 'region', 'phone', 'date_of_birth', 'profile_image', 'id_image')  # Exclude 'api_key'
    
class AccountsUserAdmin(AuthUserAdmin):
    form = CustomUserChangeForm

    superadmin_fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    user_fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'groups'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    readonly_fields = ('password',)

    def password(self, obj):
        return "********* <a href='../password/'>Change password</a>"

    password.allow_tags = True
    password.short_description = 'Password'

    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return super().get_fieldsets(request, obj)
        
        if request.user.is_superuser:
            fieldsets = self.superadmin_fieldsets
        elif request.user.groups.filter(name='Admin').exists():
            fieldsets = self.user_fieldsets
        return fieldsets
    
    def save_model(self, request, obj, form, change):
        if not change and not obj.is_superuser and not request.user.is_superuser:
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
        if user.is_superuser:
            self.inlines = [UserProfileStaffInline]
        else:
            self.inlines = [UserProfileInline]
        
        return super(AccountsUserAdmin, self).change_view(request, object_id, form_url, extra_context)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user
        if user.is_superuser:
            return qs
        api_key = user.userprofile.api_key

        if api_key:
            return qs.filter(userprofile__api_key=api_key).exclude(is_superuser=True)
        else:
            return qs.none()

admin.site.unregister(User)
admin.site.register(User, AccountsUserAdmin)
admin.site.register(ApiKey)
admin.site.register(ActionTrail)