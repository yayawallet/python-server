from rest_framework import serializers

class ContractDataSerializer(serializers.Serializer):
    row_number  = serializers.IntegerField(required=True)
    contract_number = serializers.CharField(required=True)
    service_type = serializers.CharField(required=True)
    customer_account_name = serializers.CharField(required=True)
    json_object = serializers.JSONField(required=False)
    uploaded = serializers.BooleanField(required=False)
    imported_document_id = serializers.IntegerField(required=False)