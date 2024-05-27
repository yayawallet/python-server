import uuid 
from django.db import models

class Scheduled(models.Model):
    uuid = models.UUIDField( 
         primary_key = True, 
         default = uuid.uuid4, 
         editable = False) 
    account_number = models.CharField()
    amount = models.FloatField()
    reason = models.CharField()
    recurring = models.CharField()
    start_at = models.CharField()
    meta_data = models.CharField()
    json_object = models.CharField()
    uploaded = models.BooleanField()

class Contract(models.Model):
    uuid = models.UUIDField( 
         primary_key = True, 
         default = uuid.uuid4, 
         editable = False) 
    contract_number = models.CharField()
    service_type = models.CharField()
    customer_account_name = models.CharField()
    meta_data = models.CharField()
    json_object = models.CharField()
    uploaded = models.BooleanField()

    class Meta:
        unique_together = ('contract_number', 'customer_account_name',)

class FailedContract(models.Model):
    uuid = models.UUIDField( 
         primary_key = True, 
         default = uuid.uuid4, 
         editable = False) 
    json_object = models.CharField()

class RecurringPaymentRequest(models.Model):
    uuid = models.UUIDField( 
         primary_key = True, 
         default = uuid.uuid4, 
         editable = False) 
    contract_number = models.CharField()
    amount = models.FloatField()
    currency = models.CharField()
    cause = models.CharField()
    notification_url = models.CharField()
    meta_data = models.CharField()
    json_object = models.CharField()
    uploaded = models.BooleanField()