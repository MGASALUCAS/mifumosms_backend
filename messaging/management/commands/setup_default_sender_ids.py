"""
Management command to set up default sender IDs for all tenants.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from tenants.models import Tenant
from messaging.models_sms import SMSSenderID, SMSProvider
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Set up default sender IDs and SMS providers for all tenants'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sender-id',
            type=str,
            default='Taarifa-SMS',
            help='Default sender ID to create (default: Taarifa-SMS)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update existing sender IDs'
        )

    def handle(self, *args, **options):
        sender_id = options['sender_id']
        force = options['force']
        
        self.stdout.write(f'Setting up default sender ID "{sender_id}" for all tenants...')
        
        tenants_processed = 0
        sender_ids_created = 0
        sender_ids_updated = 0
        providers_created = 0
        
        for tenant in Tenant.objects.all():
            try:
                with transaction.atomic():
                    # Create or update SMS provider
                    provider, provider_created = SMSProvider.objects.get_or_create(
                        tenant=tenant,
                        name='Default SMS Provider',
                        defaults={
                            'provider_type': 'beem',
                            'is_active': True,
                            'is_default': True,
                            'api_key': 'default_key',  # Will be updated by admin
                            'secret_key': 'default_secret',  # Will be updated by admin
                            'api_url': 'https://api.beem.africa/v1/send',
                            'cost_per_sms': 25.0,
                            'currency': 'TZS'
                        }
                    )
                    
                    if provider_created:
                        providers_created += 1
                        self.stdout.write(f'  Created SMS provider for tenant: {tenant.name}')
                    
                    # Create or update sender ID
                    sender_id_obj, sender_created = SMSSenderID.objects.get_or_create(
                        tenant=tenant,
                        sender_id=sender_id,
                        defaults={
                            'provider': provider,
                            'status': 'active',
                            'sample_content': f'This is a test message from {sender_id}'
                        }
                    )
                    
                    if sender_created:
                        sender_ids_created += 1
                        self.stdout.write(f'  Created sender ID "{sender_id}" for tenant: {tenant.name}')
                    elif force:
                        # Update existing sender ID
                        sender_id_obj.status = 'active'
                        sender_id_obj.provider = provider
                        sender_id_obj.save()
                        sender_ids_updated += 1
                        self.stdout.write(f'  Updated sender ID "{sender_id}" for tenant: {tenant.name}')
                    else:
                        self.stdout.write(f'  Sender ID "{sender_id}" already exists for tenant: {tenant.name}')
                    
                    tenants_processed += 1
                    
            except Exception as e:
                self.stderr.write(f'Error processing tenant {tenant.name}: {str(e)}')
                continue
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompleted!\n'
                f'Tenants processed: {tenants_processed}\n'
                f'Sender IDs created: {sender_ids_created}\n'
                f'Sender IDs updated: {sender_ids_updated}\n'
                f'SMS providers created: {providers_created}'
            )
        )
