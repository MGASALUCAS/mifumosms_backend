"""
Signals for billing app.
"""
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.core.management import call_command
from django.conf import settings


@receiver(post_migrate)
def setup_sms_packages(sender, **kwargs):
    """
    Automatically setup SMS packages after migrations.
    This ensures packages are always available.
    """
    # Only run for the billing app and not during tests
    if sender.name == 'billing' and not settings.TESTING:
        # Check if packages already exist
        from billing.models import SMSPackage
        
        # Only create packages if none exist
        if not SMSPackage.objects.exists():
            try:
                call_command('setup_sms_packages')
            except Exception as e:
                # Log error but don't fail the migration
                print(f"Warning: Could not setup SMS packages: {e}")
        else:
            # Packages exist, just ensure they have proper sender ID configuration
            # Only update if packages don't have sender ID configuration
            packages_without_sender_id = SMSPackage.objects.filter(
                default_sender_id__isnull=True
            )
            if packages_without_sender_id.exists():
                try:
                    call_command('setup_sms_packages', '--update')
                except Exception as e:
                    # Log error but don't fail the migration
                    print(f"Warning: Could not update SMS packages: {e}")
