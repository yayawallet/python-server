from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = 'Add permissions to a specific group'

    def handle(self, *args, **options):

        group, _ = Group.objects.get_or_create(name="Agent")

        create_user = Permission.objects.get(codename="create_user")
        create_invitation = Permission.objects.get(codename="create_invitation")
        get_invitation_otp = Permission.objects.get(codename="get_invitation_otp")

        group.permissions.add(create_user)
        group.permissions.add(create_invitation)
        group.permissions.add(get_invitation_otp)

        self.stdout.write(self.style.SUCCESS('Successfully added permissions to Agent group'))