"""
Management command to set up default sender ID for all tenants.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from tenants.models import Tenant
from messaging.models_sms import SMSProvider, SMSSenderID
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Set up default Taarifa-SMS sender ID for all tenants'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tenant-id',
            type=str,
            help='Specific tenant ID to process (optional)',
        )

    def handle(self, *args, **options):
        tenant_id = options.get('tenant_id')
        
        if tenant_id:
            tenants = Tenant.objects.filter(id=tenant_id)
            if not tenants.exists():
                self.stdout.write(
                    self.style.ERROR(f'Tenant with ID {tenant_id} not found')
                )
                return
        else:
            tenants = Tenant.objects.all()

        processed_count = 0
        created_count = 0

        for tenant in tenants:
            try:
                with transaction.atomic():
                    # Get or create Beem provider for tenant
                    beem_provider, created = SMSProvider.objects.get_or_create(
                        tenant=tenant,
                        provider_type='beem',
                        defaults={
                            'name': 'Beem Africa SMS',
                            'api_key': '',  # Will be set from environment
                            'secret_key': '',  # Will be set from environment
                            'api_url': 'https://apisms.beem.africa/v1/send',
                            'is_active': True,
                            'is_default': True,
                            'cost_per_sms': 0.05,
                            'currency': 'USD'
                        }
                    )

                    # Get or create default sender ID
                    sender_id, created = SMSSenderID.objects.get_or_create(
                        tenant=tenant,
                        sender_id='Taarifa-SMS',
                        defaults={
                            'provider': beem_provider,
                            'sample_content': 'A test use case for the sender name purposely used for information transfer.',
                            'status': 'active'
                        }
                    )

                    if created:
                        created_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Created Taarifa-SMS sender ID for tenant: {tenant.name}'
                            )
                        )
                    else:
                        self.stdout.write(
                            f'Sender ID already exists for tenant: {tenant.name}'
                        )

                    processed_count += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Error processing tenant {tenant.name}: {str(e)}'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Processed {processed_count} tenants, created {created_count} sender IDs'
            )
        )
