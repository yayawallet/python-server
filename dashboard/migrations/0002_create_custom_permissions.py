# Generated by Django 5.0.6 on 2024-06-08 08:25

from django.db import migrations

def create_custom_permissions(apps, schema_editor):
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    content_type = ContentType.objects.get_for_model(Permission)

    Permission.objects.create(
        codename='can_transfer_money',
        name='Can Transfer Money',
        content_type=content_type,
    )

    Permission.objects.create(
        codename='buy_airtime',
        name='Buy Airtime',
        content_type=content_type,
    )

    Permission.objects.create(
        codename='buy_package',
        name='Buy Package',
        content_type=content_type,
    )

    Permission.objects.create(
        codename='create_equb',
        name='Create Equb',
        content_type=content_type,
    )

    Permission.objects.create(
        codename='update_equb',
        name='Update Equb',
        content_type=content_type,
    )

    Permission.objects.create(
        codename='create_invitation',
        name='Create Invitation',
        content_type=content_type,
    )

    Permission.objects.create(
        codename='create_contract',
        name='Create Contract',
        content_type=content_type,
    )

    Permission.objects.create(
        codename='request_payment',
        name='Request Payment',
        content_type=content_type,
    )

    Permission.objects.create(
        codename='bulk_import_contract',
        name='Bulk Import Contract',
        content_type=content_type,
    )

    Permission.objects.create(
        codename='bulk_import_request_payment',
        name='Bulk Import Request Payment',
        content_type=content_type,
    )

    Permission.objects.create(
        codename='create_saving',
        name='Create Saving',
        content_type=content_type,
    )

    Permission.objects.create(
        codename='claim',
        name='Claim',
        content_type=content_type,
    )

    Permission.objects.create(
        codename='create_schedule',
        name='Create Schedule',
        content_type=content_type,
    )

    Permission.objects.create(
        codename='bulk_schedule_import',
        name='Bulk Schedule Import',
        content_type=content_type,
    )

    Permission.objects.create(
        codename='generate_qr_url',
        name='Generate QR Url',
        content_type=content_type,
    )

    Permission.objects.create(
        codename='transfer_as_user',
        name='Transfer As User',
        content_type=content_type,
    )

    Permission.objects.create(
        codename='external_account_lookup',
        name='External Account Lookup',
        content_type=content_type,
    )


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_custom_permissions),
    ]