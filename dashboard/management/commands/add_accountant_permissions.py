from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = 'Add permissions to a specific group'

    def handle(self, *args, **options):

        group, _ = Group.objects.get_or_create(name="Accountant")

        can_transfer_money = Permission.objects.get(codename="can_transfer_money")
        buy_airtime = Permission.objects.get(codename="buy_airtime")
        buy_package = Permission.objects.get(codename="buy_package")
        create_equb = Permission.objects.get(codename="create_equb")
        update_equb = Permission.objects.get(codename="update_equb")
        create_contract = Permission.objects.get(codename="create_contract")
        request_payment = Permission.objects.get(codename="request_payment")
        create_saving = Permission.objects.get(codename="create_saving")
        claim = Permission.objects.get(codename="claim")
        generate_qr_url = Permission.objects.get(codename="generate_qr_url")
        transfer_as_user = Permission.objects.get(codename="transfer_as_user")
        external_account_lookup = Permission.objects.get(codename="external_account_lookup")
        create_bill = Permission.objects.get(codename="create_bill")
        create_bulk_bill = Permission.objects.get(codename="create_bulk_bill")
        update_bill = Permission.objects.get(codename="update_bill")
        create_payout = Permission.objects.get(codename="create_payout")
        create_bulk_payout = Permission.objects.get(codename="create_bulk_payout")
        bulk_schedule_request = Permission.objects.get(codename="bulk_schedule_request")
        my_bulk_scheduled_requests = Permission.objects.get(codename="my_bulk_scheduled_requests")
        bulk_contract_request = Permission.objects.get(codename="bulk_contract_request")
        my_bulk_contract_requests = Permission.objects.get(codename="my_bulk_contract_requests")
        bulk_payment_request = Permission.objects.get(codename="bulk_payment_request")
        my_bulk_payment_requests = Permission.objects.get(codename="my_bulk_payment_requests")
        schedule_request = Permission.objects.get(codename="schedule_request")
        my_scheduled_requests = Permission.objects.get(codename="my_scheduled_requests")

        group.permissions.add(can_transfer_money)
        group.permissions.add(buy_airtime)
        group.permissions.add(buy_package)
        group.permissions.add(create_equb)
        group.permissions.add(update_equb)
        group.permissions.add(create_contract)
        group.permissions.add(request_payment)
        group.permissions.add(create_saving)
        group.permissions.add(claim)
        group.permissions.add(generate_qr_url)
        group.permissions.add(transfer_as_user)
        group.permissions.add(external_account_lookup)
        group.permissions.add(create_bill)
        group.permissions.add(create_bulk_bill)
        group.permissions.add(update_bill)
        group.permissions.add(create_payout)
        group.permissions.add(create_bulk_payout)
        group.permissions.add(bulk_schedule_request)
        group.permissions.add(my_bulk_scheduled_requests)
        group.permissions.add(bulk_contract_request)
        group.permissions.add(my_bulk_contract_requests)
        group.permissions.add(bulk_payment_request)
        group.permissions.add(my_bulk_payment_requests)
        group.permissions.add(schedule_request)
        group.permissions.add(my_scheduled_requests)

        self.stdout.write(self.style.SUCCESS('Successfully added permissions to Accountant group'))