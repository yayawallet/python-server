from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = 'Add permissions to a specific group'

    def handle(self, *args, **options):

        group, _ = Group.objects.get_or_create(name="Approver")

        approval_bulk_schedule_import = Permission.objects.get(codename="approval_bulk_schedule_import")
        bulk_scheduled_requests = Permission.objects.get(codename="bulk_scheduled_requests")
        approval_bulk_contract_import = Permission.objects.get(codename="approval_bulk_contract_import")
        bulk_contract_requests = Permission.objects.get(codename="bulk_contract_requests")
        approval_bulk_payment_request_import = Permission.objects.get(codename="approval_bulk_payment_request_import")
        bulk_requested_payments = Permission.objects.get(codename="bulk_requested_payments")
        approval_scheduled = Permission.objects.get(codename="approval_scheduled")
        scheduled_requests = Permission.objects.get(codename="scheduled_requests")

        group.permissions.add(approval_bulk_schedule_import)
        group.permissions.add(bulk_scheduled_requests)
        group.permissions.add(approval_bulk_contract_import)
        group.permissions.add(bulk_contract_requests)
        group.permissions.add(approval_bulk_payment_request_import)
        group.permissions.add(bulk_requested_payments)
        group.permissions.add(approval_scheduled)
        group.permissions.add(scheduled_requests)

        self.stdout.write(self.style.SUCCESS('Successfully added permissions to Approver group'))