from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = 'Add permissions to a specific group'

    def handle(self, *args, **options):

        group, _ = Group.objects.get_or_create(name="Admin")

        can_access_admin = Permission.objects.get(codename="can_access_admin")
        view_group = Permission.objects.get(codename="view_group")
        view_permission = Permission.objects.get(codename="view_permission")
        add_user = Permission.objects.get(codename="add_user")
        change_user = Permission.objects.get(codename="change_user")
        delete_user = Permission.objects.get(codename="delete_user")
        view_user = Permission.objects.get(codename="view_user")
        add_userprofile = Permission.objects.get(codename="add_userprofile")
        change_userprofile = Permission.objects.get(codename="change_userprofile")
        delete_userprofile = Permission.objects.get(codename="delete_userprofile")
        view_userprofile = Permission.objects.get(codename="view_userprofile")
        view_actiontrail = Permission.objects.get(codename="view_actiontrail")
        add_approverrule = Permission.objects.get(codename="add_approverrule")
        change_approverrule = Permission.objects.get(codename="change_approverrule")
        delete_approverrule = Permission.objects.get(codename="delete_approverrule")
        view_approverrule = Permission.objects.get(codename="view_approverrule")
        
        group.permissions.add(can_access_admin)
        group.permissions.add(view_group)
        group.permissions.add(view_permission)
        group.permissions.add(add_user)
        group.permissions.add(change_user)
        group.permissions.add(delete_user)
        group.permissions.add(view_user)
        group.permissions.add(add_userprofile)
        group.permissions.add(change_userprofile)
        group.permissions.add(delete_userprofile)
        group.permissions.add(view_userprofile)
        group.permissions.add(view_actiontrail)
        group.permissions.add(add_approverrule)
        group.permissions.add(change_approverrule)
        group.permissions.add(delete_approverrule)
        group.permissions.add(view_approverrule)

        self.stdout.write(self.style.SUCCESS('Successfully added permissions to Admin group'))