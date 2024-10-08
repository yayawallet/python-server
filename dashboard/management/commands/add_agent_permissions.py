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
        buy_airtime = Permission.objects.get(codename="buy_airtime")
        buy_package = Permission.objects.get(codename="buy_package")
        create_equb = Permission.objects.get(codename="create_equb")
        update_equb = Permission.objects.get(codename="update_equb")
        create_saving = Permission.objects.get(codename="create_saving")
        claim = Permission.objects.get(codename="claim")
        generate_qr_url = Permission.objects.get(codename="generate_qr_url")
        external_account_lookup = Permission.objects.get(codename="external_account_lookup")
        create_bill = Permission.objects.get(codename="create_bill")
        create_bulk_bill = Permission.objects.get(codename="create_bulk_bill")
        update_bill = Permission.objects.get(codename="update_bill")
        create_payout = Permission.objects.get(codename="create_payout")
        create_bulk_payout = Permission.objects.get(codename="create_bulk_payout")
        bulk_schedule_request = Permission.objects.get(codename="bulk_schedule_request")
        bulk_scheduled_requests = Permission.objects.get(codename="bulk_scheduled_requests")
        bulk_contract_request = Permission.objects.get(codename="bulk_contract_request")
        bulk_contract_requests = Permission.objects.get(codename="bulk_contract_requests")
        bulk_payment_request = Permission.objects.get(codename="bulk_payment_request")
        bulk_requested_payments = Permission.objects.get(codename="bulk_requested_payments")
        schedule_request = Permission.objects.get(codename="schedule_request")
        scheduled_requests = Permission.objects.get(codename="scheduled_requests")
        contract_request = Permission.objects.get(codename="contract_request")
        contract_requests = Permission.objects.get(codename="contract_requests")
        payment_request = Permission.objects.get(codename="payment_request")
        payment_requests = Permission.objects.get(codename="payment_requests")
        transaction_request = Permission.objects.get(codename="transaction_request")
        transaction_requests = Permission.objects.get(codename="transaction_requests")
        transfer_request = Permission.objects.get(codename="transfer_request")
        transfer_requests = Permission.objects.get(codename="transfer_requests")
        airtime_request = Permission.objects.get(codename="airtime_request")
        airtime_requests = Permission.objects.get(codename="airtime_requests")
        package_request = Permission.objects.get(codename="package_request")

        group.permissions.add(create_user)
        group.permissions.add(create_invitation)
        group.permissions.add(get_invitation_otp)
        group.permissions.add(buy_airtime)
        group.permissions.add(buy_package)
        group.permissions.add(create_equb)
        group.permissions.add(update_equb)
        group.permissions.add(create_saving)
        group.permissions.add(claim)
        group.permissions.add(generate_qr_url)
        group.permissions.add(external_account_lookup)
        group.permissions.add(create_bill)
        group.permissions.add(create_bulk_bill)
        group.permissions.add(update_bill)
        group.permissions.add(create_payout)
        group.permissions.add(create_bulk_payout)
        group.permissions.add(bulk_schedule_request)
        group.permissions.add(bulk_scheduled_requests)
        group.permissions.add(bulk_contract_request)
        group.permissions.add(bulk_contract_requests)
        group.permissions.add(bulk_payment_request)
        group.permissions.add(bulk_requested_payments)
        group.permissions.add(schedule_request)
        group.permissions.add(scheduled_requests)
        group.permissions.add(contract_request)
        group.permissions.add(contract_requests)
        group.permissions.add(payment_request)
        group.permissions.add(payment_requests)
        group.permissions.add(transaction_request)
        group.permissions.add(transaction_requests)
        group.permissions.add(transfer_request)
        group.permissions.add(transfer_requests)
        group.permissions.add(airtime_request)
        group.permissions.add(airtime_requests)
        group.permissions.add(package_request)

        self.stdout.write(self.style.SUCCESS('Successfully added permissions to Agent group'))