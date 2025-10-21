"""
Management command to set up shared sender ID system.
This ensures all users use the same 'Taarifa-SMS' sender ID but have individual SMS credits.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from tenants.models import Tenant, Membership
from messaging.models_sms import SMSProvider, SMSSenderID
from billing.models import SMSBalance

User = get_user_model()


class Command(BaseCommand):
    help = 'Set up shared sender ID system for all tenants'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update existing sender IDs to shared sender ID',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up shared sender ID system...'))
        
        force_update = options['force']
        shared_sender_id = "Taarifa-SMS"
        
        # Get all tenants
        tenants = Tenant.objects.all()
        self.stdout.write(f'Found {tenants.count()} tenants')
        
        updated_count = 0
        created_count = 0
        
        for tenant in tenants:
            self.stdout.write(f'\nProcessing tenant: {tenant.name}')
            
            # Get or create SMS provider (handle multiple providers)
            sms_provider = SMSProvider.objects.filter(
                tenant=tenant,
                provider_type='beem'
            ).first()
            
            if not sms_provider:
                sms_provider = SMSProvider.objects.create(
                    tenant=tenant,
                    provider_type='beem',
                    name='Default Beem Provider',
                    is_active=True,
                    is_default=True,
                    api_key='',  # Will be configured later
                    secret_key='',  # Will be configured later
                    api_url='https://apisms.beem.africa/v1/send',
                    cost_per_sms=0.0,
                    currency='TZS',
                    created_by=tenant.memberships.filter(role='owner').first().user if tenant.memberships.filter(role='owner').exists() else None
                )
                provider_created = True
            else:
                provider_created = False
            
            if provider_created:
                self.stdout.write(f'  Created SMS provider for {tenant.name}')
            
            # Check if shared sender ID already exists
            existing_sender_id = SMSSenderID.objects.filter(
                tenant=tenant,
                sender_id=shared_sender_id
            ).first()
            
            if existing_sender_id:
                if force_update:
                    existing_sender_id.status = 'active'
                    existing_sender_id.sample_content = "A test use case for the sender name purposely used for information transfer."
                    existing_sender_id.save()
                    self.stdout.write(f'  Updated existing sender ID to {shared_sender_id}')
                    updated_count += 1
                else:
                    self.stdout.write(f'  Sender ID {shared_sender_id} already exists')
            else:
                # Create shared sender ID
                SMSSenderID.objects.create(
                    tenant=tenant,
                    sender_id=shared_sender_id,
                    provider=sms_provider,
                    status='active',
                    sample_content="A test use case for the sender name purposely used for information transfer.",
                    created_by=tenant.memberships.filter(role='owner').first().user if tenant.memberships.filter(role='owner').exists() else None
                )
                self.stdout.write(f'  Created shared sender ID: {shared_sender_id}')
                created_count += 1
            
            # Ensure SMS balance exists (with zero credits if new)
            sms_balance, balance_created = SMSBalance.objects.get_or_create(
                tenant=tenant,
                defaults={
                    'credits': 0,
                    'total_purchased': 0,
                    'total_used': 0
                }
            )
            
            if balance_created:
                self.stdout.write(f'  Created SMS balance with 0 credits')
            else:
                self.stdout.write(f'  SMS balance exists: {sms_balance.credits} credits')
        
        # Summary
        self.stdout.write(self.style.SUCCESS(f'\n=== Shared Sender ID Setup Complete ==='))
        self.stdout.write(f'Total tenants processed: {tenants.count()}')
        self.stdout.write(f'New sender IDs created: {created_count}')
        self.stdout.write(f'Existing sender IDs updated: {updated_count}')
        self.stdout.write(f'Shared sender ID: {shared_sender_id}')
        self.stdout.write(f'\nAll users now use the same sender ID but have individual SMS credits.')
        self.stdout.write(f'Users must purchase SMS packages to get credits for sending SMS.')
