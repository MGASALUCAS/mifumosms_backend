"""
Management command to clean up dummy API keys and webhooks.
Removes all inactive/revoked keys and webhooks, keeps only active ones.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from api_integration.models import APIKey, Webhook, APIAccount

User = get_user_model()


class Command(BaseCommand):
    help = 'Clean up dummy API keys and webhooks, keeping only one active set'

    def add_arguments(self, parser):
        parser.add_argument(
            '--keep',
            type=int,
            default=1,
            help='Number of active API keys to keep per user (default: 1)',
        )
        parser.add_argument(
            '--delete-webhooks',
            action='store_true',
            help='Delete all webhooks',
        )
        parser.add_argument(
            '--keep-latest',
            action='store_true',
            help='Keep only the latest API key',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force deletion without confirmation',
        )

    def handle(self, *args, **options):
        keep_count = options['keep']
        delete_webhooks = options['delete_webhooks']
        keep_latest = options['keep_latest']
        force = options['force']

        if not force:
            self.stdout.write(self.style.WARNING(
                'This will delete inactive API keys and webhooks.'
            ))
            response = input('Are you sure you want to continue? (yes/no): ')
            if response.lower() != 'yes':
                self.stdout.write(self.style.WARNING('Operation cancelled.'))
                return

        # Delete revoked/inactive API keys
        revoked_keys = APIKey.objects.filter(status='revoked')
        inactive_keys = APIKey.objects.filter(status__in=['revoked', 'expired'])
        
        revoked_count = revoked_keys.count()
        inactive_count = inactive_keys.count()
        
        self.stdout.write(f'Found {revoked_count} revoked API keys')
        self.stdout.write(f'Found {inactive_count} inactive/expired API keys')
        
        # Delete revoked keys
        revoked_keys.delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {revoked_count} revoked API keys'))
        
        # Delete inactive keys (keep only active if specified)
        if keep_latest:
            # For each API account, keep only the latest active key
            api_accounts = APIAccount.objects.all()
            deleted_count = 0
            
            for account in api_accounts:
                active_keys = APIKey.objects.filter(
                    api_account=account,
                    status='active',
                    is_active=True
                ).order_by('-created_at')
                
                # Keep only the latest one
                total_active = active_keys.count()
                if total_active > 1:
                    keys_to_delete = active_keys[1:]
                    deleted_count += total_active - 1
                    
                    for key in keys_to_delete:
                        key.delete()
            
            self.stdout.write(self.style.SUCCESS(
                f'Deleted {deleted_count} old active API keys (kept latest only)'
            ))
        
        # Delete all webhooks if requested
        if delete_webhooks:
            webhooks = Webhook.objects.all()
            webhook_count = webhooks.count()
            webhooks.delete()
            self.stdout.write(self.style.SUCCESS(f'Deleted {webhook_count} webhooks'))
        else:
            webhook_count = Webhook.objects.count()
            self.stdout.write(f'Found {webhook_count} webhooks (not deleted, use --delete-webhooks to delete)')

        # Show remaining items
        remaining_keys = APIKey.objects.filter(status='active', is_active=True).count()
        remaining_webhooks = Webhook.objects.filter(is_active=True).count()
        
        self.stdout.write(self.style.SUCCESS('\nCleanup complete!'))
        self.stdout.write(f'Remaining active API keys: {remaining_keys}')
        self.stdout.write(f'Remaining active webhooks: {remaining_webhooks}')

