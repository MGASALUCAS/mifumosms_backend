"""
Management command to sync payment status from Zenopay for all pending payments.
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from billing.models import PaymentTransaction
from billing.zenopay_service import zenopay_service
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sync payment status from Zenopay for all pending payments'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tenant-id',
            type=str,
            help='Sync payments for specific tenant only',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force sync even if webhook verification is enabled',
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting payment status sync...')
        
        # Get pending payments
        pending_payments = PaymentTransaction.objects.filter(status='pending')
        
        if options['tenant_id']:
            pending_payments = pending_payments.filter(tenant_id=options['tenant_id'])
            self.stdout.write(f'Syncing payments for tenant: {options["tenant_id"]}')
        
        total_payments = pending_payments.count()
        self.stdout.write(f'Found {total_payments} pending payments to sync')
        
        if total_payments == 0:
            self.stdout.write('No pending payments found.')
            return
        
        updated = 0
        failed = 0
        errors = 0
        
        for payment in pending_payments:
            try:
                self.stdout.write(f'Checking payment {payment.id} (Order: {payment.zenopay_order_id})')
                
                # Check payment status with Zenopay
                status_response = zenopay_service.check_payment_status(payment.zenopay_order_id) or {}
                
                if status_response.get('success'):
                    result = (status_response.get('payment_status') or '').upper()
                    payment_data = status_response.get('data', {}).get('data', [{}])[0] if status_response.get('data', {}).get('data') else {}
                    payment_status = payment_data.get('payment_status', '').upper()
                    
                    self.stdout.write(f'  Zenopay status: {result}, Payment status: {payment_status}')
                    
                    if result == 'SUCCESS' and payment_status == 'COMPLETED':
                        # Check if webhook verification is required
                        require_webhook = getattr(settings, 'ZENOPAY_REQUIRE_WEBHOOK', False)
                        
                        if not require_webhook or options['force'] or getattr(payment, 'webhook_received', False):
                            payment.mark_as_completed(status_response.get('data', {}))
                            if getattr(payment, 'purchase', None):
                                payment.purchase.complete_purchase()
                            updated += 1
                            self.stdout.write(f'  [SUCCESS] Updated to COMPLETED')
                        else:
                            self.stdout.write(f'  [WAITING] Waiting for webhook verification')
                            
                    elif result == 'FAILED' or payment_status == 'FAILED' or payment_status == 'CANCELLED':
                        if payment_status == 'CANCELLED':
                            payment.mark_as_failed('Payment cancelled by user or expired via sync')
                            self.stdout.write(f'  [CANCELLED] Marked as CANCELLED')
                        else:
                            payment.mark_as_failed('Payment failed via sync')
                            self.stdout.write(f'  [FAILED] Marked as FAILED')
                        if getattr(payment, 'purchase', None):
                            payment.purchase.mark_as_failed()
                        updated += 1
                    else:
                        self.stdout.write(f'  [PENDING] Still pending (Status: {payment_status or result})')
                else:
                    failed += 1
                    error_msg = status_response.get('error', 'Unknown error')
                    self.stdout.write(f'  [ERROR] Failed to check status: {error_msg}')
                    
            except Exception as e:
                errors += 1
                self.stdout.write(f'  [ERROR] Error processing payment {payment.id}: {str(e)}')
                logger.exception(f'Error processing payment {payment.id}')
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write('SYNC SUMMARY:')
        self.stdout.write(f'Total payments checked: {total_payments}')
        self.stdout.write(f'Successfully updated: {updated}')
        self.stdout.write(f'Failed to check: {failed}')
        self.stdout.write(f'Errors: {errors}')
        
        if updated > 0:
            self.stdout.write(f'\n[SUCCESS] {updated} payments have been updated!')
        else:
            self.stdout.write('\n[WARNING] No payments were updated. This could mean:')
            self.stdout.write('   - Payments are still pending on Zenopay')
            self.stdout.write('   - Webhook verification is required (use --force to override)')
            self.stdout.write('   - Zenopay API is not responding')
