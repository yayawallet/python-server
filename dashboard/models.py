import uuid 
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db.models import Q
from django.db.models.signals import m2m_changed

class ApiKey(models.Model):
    uuid = models.UUIDField( 
         primary_key = True, 
         default = uuid.uuid4, 
         editable = False)
    name = models.CharField()
    api_key = models.CharField()

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    country = models.CharField(null=True, blank=True)
    address = models.CharField(null=True, blank=True)
    region = models.CharField(null=True, blank=True)
    phone = models.CharField()
    date_of_birth = models.DateField(null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    id_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    api_key = models.ForeignKey(ApiKey, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.user.username
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(m2m_changed, sender=User.groups.through)
def group_change_handler(sender, instance, **kwargs):
    if kwargs['action'] in ['post_add', 'post_remove', 'post_clear']:
        instance.save()
        print(instance)
        usear = User.objects.get(username='ermiyas')
        print(usear.has_perm('dashboard.can_access_admin'))
        print(usear.groups.filter(permissions__codename='can_access_admin').exists())
        if instance.groups.filter(permissions__codename='can_access_admin').exists() or instance.has_perm('dashboard.can_access_admin'):
            instance.is_staff = True
            print("third check")
        else:
            instance.is_staff = False
        instance.save()
        print("final check")

class ImportedDocuments(models.Model):
    uuid = models.UUIDField( 
         primary_key = True, 
         default = uuid.uuid4, 
         editable = False)
    file_name = models.CharField()
    remark = models.CharField()
    import_type = models.CharField()
    failed_count = models.IntegerField(null=True, blank=True)
    successful_count = models.IntegerField(null=True, blank=True)
    on_queue_count = models.IntegerField(null=True, blank=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

SCHEDULING_CHOICES = [
    ('draft', 'Draft'),
    ('published', 'Published'),
    ('archived', 'Archived'),
]

class Scheduled(models.Model):
    SCHEDULING_CHOICES = [
        ('once', 'once'),
        ('daily', 'daily'),
        ('weekly', 'weekly'),
        ('monthly', 'monthly'),
    ]
    uuid = models.UUIDField( 
         primary_key = True, 
         default = uuid.uuid4, 
         editable = False) 
    row_number = models.IntegerField()
    account_number = models.CharField()
    amount = models.FloatField()
    reason = models.CharField()
    recurring = models.CharField(
        max_length=10,
        choices=SCHEDULING_CHOICES,
    )
    start_at = models.CharField()
    meta_data = models.CharField()
    json_object = models.CharField()
    uploaded = models.BooleanField()
    imported_document_id = models.ForeignKey(ImportedDocuments, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(recurring__in=['once', 'daily', 'weekly', 'monthly']),
                name='recurring_valid_values'
            ),
        ]

class Contract(models.Model):
    uuid = models.UUIDField( 
         primary_key = True, 
         default = uuid.uuid4, 
         editable = False) 
    row_number = models.IntegerField()
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
        unique_together = ('contract_number', 'service_type',)

class FailedImports(models.Model):
    uuid = models.UUIDField( 
         primary_key = True, 
         default = uuid.uuid4, 
         editable = False) 
    row_number = models.IntegerField()
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
    row_number = models.IntegerField()
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

class Bill(models.Model):
    uuid = models.UUIDField( 
         primary_key = True, 
         default = uuid.uuid4, 
         editable = False) 
    row_number = models.IntegerField(null=True, blank=True)
    client_yaya_account = models.CharField(null=True, blank=True)
    customer_yaya_account = models.CharField(null=True, blank=True)
    amount = models.FloatField(null=True, blank=True)
    start_at = models.IntegerField(null=True, blank=True)
    due_at = models.IntegerField(null=True, blank=True)
    customer_id = models.CharField(null=True, blank=True)
    bill_id = models.CharField(null=True, blank=True)
    bill_code = models.CharField(null=True, blank=True)
    bill_season = models.CharField(null=True, blank=True)
    cluster = models.CharField(null=True, blank=True)
    description = models.CharField(null=True, blank=True)
    phone = models.CharField(null=True, blank=True)
    email = models.CharField(null=True, blank=True)
    details = models.CharField(null=True, blank=True)
    json_object = models.CharField(null=True, blank=True)
    uploaded = models.BooleanField(null=True, blank=True)
    imported_document_id = models.ForeignKey(ImportedDocuments, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Payout(models.Model):
    uuid = models.UUIDField( 
         primary_key = True, 
         default = uuid.uuid4, 
         editable = False) 
    row_number = models.IntegerField(null=True, blank=True)
    client_yaya_account = models.CharField(null=True, blank=True)
    cluster = models.CharField(null=True, blank=True)
    bill_code = models.CharField(null=True, blank=True)
    institution = models.CharField(null=True, blank=True)
    account_number = models.CharField(null=True, blank=True)
    details = models.CharField(null=True, blank=True)
    json_object = models.CharField(null=True, blank=True)
    uploaded = models.BooleanField(null=True, blank=True)
    imported_document_id = models.ForeignKey(ImportedDocuments, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ActionTrail(models.Model):
    uuid = models.UUIDField( 
         primary_key = True, 
         default = uuid.uuid4, 
         editable = False) 
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    action_id = models.CharField()
    action_type = models.CharField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        created_at_str = self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        return self.user_id.username + ' - ' + self.action_type + ' (' + created_at_str + ')'

class BillSlice(models.Model):
    uuid = models.UUIDField( 
         primary_key = True, 
         default = uuid.uuid4, 
         editable = False) 
    slice_upload_id = models.CharField()
    imported_document_id = models.ForeignKey(ImportedDocuments, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class RejectedRequest(models.Model):
    uuid = models.UUIDField( 
         primary_key = True, 
         default = uuid.uuid4, 
         editable = False) 
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rejection_reason = models.CharField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ApprovalRequest(models.Model):
    uuid = models.UUIDField( 
         primary_key = True, 
         default = uuid.uuid4, 
         editable = False) 
    requesting_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    request_type = models.CharField()
    file = models.FileField(upload_to='uploads/', null=True, blank=True)
    remark = models.CharField(null=True, blank=True)
    approved_by = models.ManyToManyField(User, related_name='approved_requests', blank=True)
    rejected_by = models.ManyToManyField(RejectedRequest, related_name='rejected_requests', blank=True)
    approvers = models.ManyToManyField(User, related_name='approvers', blank=True)
    request_json = models.JSONField(null=True, blank=True)
    is_successful = models.BooleanField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ApproverRule(models.Model):
    uuid = models.UUIDField( 
         primary_key = True, 
         default = uuid.uuid4, 
         editable = False) 
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    approve_threshold = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.user.username