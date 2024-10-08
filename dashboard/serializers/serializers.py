from rest_framework import serializers
from django.contrib.auth.models import User
from ..models import Scheduled, Contract, FailedImports, ImportedDocuments, RecurringPaymentRequest, UserProfile, Bill, Payout, ApprovalRequest, RejectedRequest


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name']

class UserExtendedSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'last_login', 'is_superuser', 'username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'date_joined']

class ImportedDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportedDocuments 
        fields = '__all__'

class ScheduledSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scheduled 
        fields = '__all__'

class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract 
        fields = '__all__'
        
class FailedImportsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FailedImports 
        fields = '__all__'

class RecurringPaymentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecurringPaymentRequest 
        fields = '__all__'

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = UserProfile 
        fields = ['phone', 'user']

class UserProfileExtendedSerializer(serializers.ModelSerializer):
    user = UserExtendedSerializer()
    class Meta:
        model = UserProfile 
        fields = ['id', 'user', 'country', 'address', 'region', 'phone', 'date_of_birth', 'profile_image', 'id_image']

class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = '__all__'

class PayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payout
        fields = '__all__'

class RejectedRequestSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = RejectedRequest
        fields = ['user', 'rejection_reason']

class ApprovalRequestSerializer(serializers.ModelSerializer):
    requesting_user = UserProfileSerializer(many=False, read_only=True)
    approved_by = UserSerializer(many=True, read_only=True)
    rejected_by = RejectedRequestSerializer(many=True, read_only=True)
    approvers = UserSerializer(many=True, read_only=True)

    class Meta:
        model = ApprovalRequest
        fields = '__all__' 