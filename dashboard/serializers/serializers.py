from rest_framework import serializers
from ..models import Scheduled, Contract, FailedContract, RecurringPaymentRequest

class ScheduledSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scheduled 
        fields = '__all__'

class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract 
        fields = '__all__'
        
class FailedContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = FailedContract 
        fields = '__all__'

class RecurringPaymentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecurringPaymentRequest 
        fields = '__all__'