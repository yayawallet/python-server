import uuid 
from django.db import models

class Scheduled(models.Model):
    uuid = models.UUIDField( 
         primary_key = True, 
         default = uuid.uuid4, 
         editable = False) 
    account_number = models.CharField()
    amount = models.CharField()
    reason = models.CharField()
    recurring = models.CharField()
    start_at = models.CharField()
    meta_data = models.CharField()
    json_object = models.CharField()
    uploaded = models.BooleanField()