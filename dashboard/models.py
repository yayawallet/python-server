import uuid 
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    api_key = models.CharField()

    def __str__(self):
        return self.user.username
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

class ImportedDocuments(models.Model):
    uuid = models.UUIDField( 
         primary_key = True, 
         default = uuid.uuid4, 
         editable = False)
    file_name = models.CharField()
    remark = models.CharField()
    import_type = models.CharField()
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    imported_document_id = models.ForeignKey(ImportedDocuments, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    imported_document_id = models.ForeignKey(ImportedDocuments, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('contract_number', 'customer_account_name',)

class FailedImports(models.Model):
    uuid = models.UUIDField( 
         primary_key = True, 
         default = uuid.uuid4, 
         editable = False) 
    json_object = models.CharField()
    error_message = models.CharField()
    imported_document_id = models.ForeignKey(ImportedDocuments, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


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
    imported_document_id = models.ForeignKey(ImportedDocuments, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)