from rest_framework import serializers
from ..models import Scheduled, Contract, FailedImports, ImportedDocuments, RecurringPaymentRequest, UserProfile, Bill

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
    class Meta:
        model = UserProfile 
        fields = '__all__'

class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = '__all__'