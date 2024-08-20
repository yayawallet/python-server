from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = 'Add permissions to a specific group'

    def handle(self, *args, **options):

        group, _ = Group.objects.get_or_create(name="Approver")

        approval_bulk_schedule_import = Permission.objects.get(codename="approval_bulk_schedule_import")

        group.permissions.add(approval_bulk_schedule_import)

        self.stdout.write(self.style.SUCCESS('Successfully added permissions to Approver group'))