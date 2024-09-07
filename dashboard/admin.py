# admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, ApiKey, ActionTrail, ApproverRule, ApprovalRequest
from django.contrib.auth.models import Group
from django import forms
from .forms.custom_user_change_form import CustomUserChangeForm

class UserProfileStaffInline(admin.StackedInline):
    model = UserProfile
    can_delete = False

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    fields = ('country', 'address', 'region', 'phone', 'date_of_birth', 'profile_image', 'id_image')
    
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

        if api_key and request.user.groups.filter(name='Admin').exists():
            return qs.filter(userprofile__api_key=api_key).exclude(is_superuser=True)
        else:
            return qs.none()
        
class ActionTrailAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user
        api_key = user.userprofile.api_key
        if user.is_superuser:
            return qs
        elif request.user.groups.filter(name='Admin').exists():
            return qs.filter(user_id__userprofile__api_key=api_key).exclude(user_id__is_superuser=True)
        return qs.none()
    
class ApproverRuleAdminForm(forms.ModelForm):
    class Meta:
        model = ApproverRule
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        if 'user' in self.fields:
            user = self.request.user
            api_key = user.userprofile.api_key
            is_superuser = user.is_superuser
            approver_group = Group.objects.get(name='Approver')
            approvers_in_group = UserProfile.objects.filter(
                user__groups=approver_group
            )
            approvers_already_assigned = ApproverRule.objects.values_list('user', flat=True)
            if(is_superuser):
                self.fields['user'].queryset = approvers_in_group.exclude(id__in=approvers_already_assigned)
            else:
                self.fields['user'].queryset = approvers_in_group.filter(api_key=api_key).exclude(id__in=approvers_already_assigned)

class ApproverRuleAdmin(admin.ModelAdmin):
    form = ApproverRuleAdminForm

    def get_form(self, request, obj=None, **kwargs):
        form_class = super().get_form(request, obj, **kwargs)
        
        class RequestForm(form_class):
            def __init__(self, *args, **kwargs):
                kwargs['request'] = request
                super().__init__(*args, **kwargs)

        return RequestForm

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True

    def has_view_permission(self, request, obj=None):
        return True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user
        api_key = user.userprofile.api_key
        if user.is_superuser:
            return qs
        elif request.user.groups.filter(name='Admin').exists():
            return qs.filter(user__api_key=api_key).exclude(user__user__is_superuser=True)
        return qs.none()
    
class ApprovalRequestAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user
        api_key = user.userprofile.api_key
        if user.is_superuser:
            return qs
        elif request.user.groups.filter(name='Admin').exists():
            return qs.filter(requesting_user__api_key=api_key).exclude(requesting_user__user__is_superuser=True)
        return qs.none()
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return [f.name for f in self.model._meta.fields]
        return super().get_readonly_fields(request, obj)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        self.readonly_fields = self.get_readonly_fields(request)
        return super().change_view(request, object_id, form_url, extra_context)

admin.site.unregister(User)
admin.site.register(User, AccountsUserAdmin)
admin.site.register(ApiKey)
admin.site.register(ApproverRule, ApproverRuleAdmin)
admin.site.register(ActionTrail, ActionTrailAdmin)
admin.site.register(ApprovalRequest, ApprovalRequestAdmin)