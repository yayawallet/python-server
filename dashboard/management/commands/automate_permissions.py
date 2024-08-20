from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import migrations

class Command(BaseCommand):
    help = 'Automates model migrations and assigns permissions to groups'

    def handle(self, *args, **options):
        call_command('makemigrations')

        call_command('migrate')

        call_command('add_accountant_permissions')

        call_command('add_admin_permissions')

        call_command('add_clerk_permissions')

        call_command('add_agent_permissions')      

        call_command('add_approver_permissions')    