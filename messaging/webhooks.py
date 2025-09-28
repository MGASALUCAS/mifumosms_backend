"""
Webhook handlers for external services.
"""
import json
import logging
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.conf import settings
from .services.whatsapp import WhatsAppService
from .tasks import process_inbound_message_task, sync_delivery_status_task
import hmac
import hashlib

logger = logging.getLogger(__name__)


class WhatsAppWebhookView(View):
    """
    Webhook view for WhatsApp Business Cloud API.
    """
    
    @method_decorator(csrf_exempt)
    @method_decorator(require_http_methods(["GET", "POST"]))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        """
        Handle webhook verification.
        """
        try:
            mode = request.GET.get('hub.mode')
            token = request.GET.get('hub.verify_token')
            challenge = request.GET.get('hub.challenge')
            
            whatsapp_service = WhatsAppService()
            verified_challenge = whatsapp_service.verify_webhook(mode, token, challenge)
            
            if verified_challenge:
                logger.info("WhatsApp webhook verified successfully")
                return HttpResponse(verified_challenge)
            else:
                logger.warning("WhatsApp webhook verification failed")
                return HttpResponse("Verification failed", status=403)
        
        except Exception as e:
            logger.error(f"Error verifying WhatsApp webhook: {str(e)}")
            return HttpResponse("Verification error", status=500)
    
    def post(self, request):
        """
        Handle incoming webhook events.
        """
        try:
            # Verify webhook signature if configured
            if not self._verify_signature(request):
                logger.warning("WhatsApp webhook signature verification failed")
                return HttpResponse("Signature verification failed", status=403)
            
            # Parse webhook payload
            payload = json.loads(request.body)
            whatsapp_service = WhatsAppService()
            parsed_data = whatsapp_service.parse_webhook(payload)
            
            if parsed_data['type'] == 'message':
                # Process incoming message
                self._process_inbound_message(parsed_data)
            
            elif parsed_data['type'] == 'status':
                # Process status update
                self._process_status_update(parsed_data)
            
            else:
                logger.info(f"Received unknown webhook type: {parsed_data['type']}")
            
            return HttpResponse("OK", status=200)
        
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in webhook payload: {str(e)}")
            return HttpResponse("Invalid JSON", status=400)
        
        except Exception as e:
            logger.error(f"Error processing WhatsApp webhook: {str(e)}")
            return HttpResponse("Processing error", status=500)
    
    def _verify_signature(self, request):
        """
        Verify webhook signature.
        """
        try:
            signature = request.META.get('HTTP_X_HUB_SIGNATURE_256', '')
            if not signature:
                return True  # Skip verification if no signature
            
            # Get the raw body
            body = request.body
            
            # Calculate expected signature
            expected_signature = 'sha256=' + hmac.new(
                settings.WA_VERIFY_TOKEN.encode('utf-8'),
                body,
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            return hmac.compare_digest(signature, expected_signature)
        
        except Exception as e:
            logger.error(f"Error verifying webhook signature: {str(e)}")
            return False
    
    def _process_inbound_message(self, data):
        """
        Process incoming message from webhook.
        """
        try:
            # Extract message data
            message_data = {
                'contact_phone': data['contact_phone'],
                'text': data['text'],
                'media_url': data.get('media_url'),
                'media_type': data.get('media_type'),
                'message_id': data['message_id'],
                'timestamp': data['timestamp']
            }
            
            # Find tenant by phone number (this is a simplified approach)
            # In production, you might want to use a more sophisticated tenant resolution
            from tenants.models import Tenant
            tenant = Tenant.objects.filter(wa_phone_number=data['contact_phone']).first()
            
            if not tenant:
                # Try to find tenant by subdomain in the webhook URL or other means
                # For now, we'll use the first active tenant (not recommended for production)
                tenant = Tenant.objects.filter(is_active=True).first()
            
            if tenant:
                message_data['tenant_id'] = str(tenant.id)
                
                # Queue message processing
                process_inbound_message_task.delay(message_data)
                
                logger.info(f"Inbound message queued for processing: {data['message_id']}")
            else:
                logger.warning(f"No tenant found for incoming message: {data['contact_phone']}")
        
        except Exception as e:
            logger.error(f"Error processing inbound message: {str(e)}")
    
    def _process_status_update(self, data):
        """
        Process message status update from webhook.
        """
        try:
            # Queue status sync
            sync_delivery_status_task.delay(
                data['message_id'],
                provider='whatsapp'
            )
            
            logger.info(f"Status update queued for sync: {data['message_id']}")
        
        except Exception as e:
            logger.error(f"Error processing status update: {str(e)}")


@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    """
    Handle Stripe webhook events.
    """
    try:
        import stripe
        from django.conf import settings
        
        # Set Stripe API key
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        # Get the webhook signature
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        payload = request.body
        
        # Verify webhook signature
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            logger.error(f"Invalid payload: {str(e)}")
            return HttpResponse("Invalid payload", status=400)
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {str(e)}")
            return HttpResponse("Invalid signature", status=400)
        
        # Handle the event
        if event['type'] == 'customer.subscription.created':
            handle_subscription_created(event['data']['object'])
        elif event['type'] == 'customer.subscription.updated':
            handle_subscription_updated(event['data']['object'])
        elif event['type'] == 'customer.subscription.deleted':
            handle_subscription_deleted(event['data']['object'])
        elif event['type'] == 'invoice.payment_succeeded':
            handle_payment_succeeded(event['data']['object'])
        elif event['type'] == 'invoice.payment_failed':
            handle_payment_failed(event['data']['object'])
        else:
            logger.info(f"Unhandled event type: {event['type']}")
        
        return HttpResponse("OK", status=200)
    
    except Exception as e:
        logger.error(f"Error processing Stripe webhook: {str(e)}")
        return HttpResponse("Processing error", status=500)


def handle_subscription_created(subscription):
    """Handle subscription created event."""
    try:
        from billing.models import Subscription, Plan
        
        # Get tenant by customer ID
        customer_id = subscription['customer']
        tenant = get_tenant_by_stripe_customer_id(customer_id)
        
        if tenant:
            # Get plan
            plan = Plan.objects.get(stripe_price_id=subscription['items']['data'][0]['price']['id'])
            
            # Create subscription record
            Subscription.objects.create(
                tenant=tenant,
                plan=plan,
                stripe_subscription_id=subscription['id'],
                status=subscription['status'],
                current_period_start=subscription['current_period_start'],
                current_period_end=subscription['current_period_end']
            )
            
            logger.info(f"Subscription created for tenant: {tenant.name}")
    
    except Exception as e:
        logger.error(f"Error handling subscription created: {str(e)}")


def handle_subscription_updated(subscription):
    """Handle subscription updated event."""
    try:
        from billing.models import Subscription
        
        # Update subscription
        sub = Subscription.objects.get(stripe_subscription_id=subscription['id'])
        sub.status = subscription['status']
        sub.current_period_start = subscription['current_period_start']
        sub.current_period_end = subscription['current_period_end']
        sub.save()
        
        logger.info(f"Subscription updated: {subscription['id']}")
    
    except Subscription.DoesNotExist:
        logger.warning(f"Subscription not found: {subscription['id']}")
    except Exception as e:
        logger.error(f"Error handling subscription updated: {str(e)}")


def handle_subscription_deleted(subscription):
    """Handle subscription deleted event."""
    try:
        from billing.models import Subscription
        
        # Update subscription status
        sub = Subscription.objects.get(stripe_subscription_id=subscription['id'])
        sub.status = 'cancelled'
        sub.save()
        
        logger.info(f"Subscription cancelled: {subscription['id']}")
    
    except Subscription.DoesNotExist:
        logger.warning(f"Subscription not found: {subscription['id']}")
    except Exception as e:
        logger.error(f"Error handling subscription deleted: {str(e)}")


def handle_payment_succeeded(invoice):
    """Handle successful payment event."""
    try:
        from billing.models import Invoice
        
        # Create invoice record
        Invoice.objects.create(
            stripe_invoice_id=invoice['id'],
            amount_paid=invoice['amount_paid'],
            currency=invoice['currency'],
            status='paid',
            paid_at=invoice['status_transitions']['paid_at']
        )
        
        logger.info(f"Payment succeeded: {invoice['id']}")
    
    except Exception as e:
        logger.error(f"Error handling payment succeeded: {str(e)}")


def handle_payment_failed(invoice):
    """Handle failed payment event."""
    try:
        from billing.models import Invoice
        
        # Create invoice record
        Invoice.objects.create(
            stripe_invoice_id=invoice['id'],
            amount_due=invoice['amount_due'],
            currency=invoice['currency'],
            status='payment_failed',
            due_date=invoice['due_date']
        )
        
        logger.info(f"Payment failed: {invoice['id']}")
    
    except Exception as e:
        logger.error(f"Error handling payment failed: {str(e)}")


def get_tenant_by_stripe_customer_id(customer_id):
    """Get tenant by Stripe customer ID."""
    try:
        from tenants.models import Tenant
        return Tenant.objects.get(stripe_customer_id=customer_id)
    except Tenant.DoesNotExist:
        return None


# URL patterns for webhooks
from django.urls import path

urlpatterns = [
    path('whatsapp/', WhatsAppWebhookView.as_view(), name='whatsapp-webhook'),
    path('stripe/', stripe_webhook, name='stripe-webhook'),
]