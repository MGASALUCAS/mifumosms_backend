"""
Celery tasks for messaging functionality.
"""
from celery import shared_task
from django.utils import timezone
from django.db import transaction
from .models import Message, Conversation, Contact, Campaign, Flow
from .services.whatsapp import WhatsAppService
from .services.ai import AIService
from .services.costmeter import CostMeterService
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_message_task(self, message_id):
    """
    Send a message via the appropriate provider.
    """
    try:
        message = Message.objects.get(id=message_id)
        
        # Check if contact is opted in
        if not message.conversation.contact.is_opted_in:
            message.mark_failed("Contact has not opted in")
            return
        
        # Send via WhatsApp
        if message.provider == 'whatsapp':
            whatsapp_service = WhatsAppService()
            result = whatsapp_service.send_message(
                to=message.conversation.contact.phone_e164,
                text=message.text,
                media_url=message.media_url if message.media_url else None
            )
            
            if result['success']:
                message.provider_message_id = result['message_id']
                message.mark_sent()
                
                # Calculate cost
                cost_service = CostMeterService()
                message.cost_micro = cost_service.calculate_message_cost(message)
                message.save()
                
                logger.info(f"Message {message_id} sent successfully")
            else:
                message.mark_failed(result['error'])
                logger.error(f"Failed to send message {message_id}: {result['error']}")
        
        # Send via SMS (if configured)
        elif message.provider == 'sms':
            # TODO: Implement SMS sending
            message.mark_failed("SMS provider not implemented")
        
        # Send via Telegram (if configured)
        elif message.provider == 'telegram':
            # TODO: Implement Telegram sending
            message.mark_failed("Telegram provider not implemented")
        
        else:
            message.mark_failed(f"Unknown provider: {message.provider}")
    
    except Message.DoesNotExist:
        logger.error(f"Message {message_id} not found")
    except Exception as exc:
        logger.error(f"Error sending message {message_id}: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def sync_delivery_status_task(self, provider_message_id, provider='whatsapp'):
    """
    Sync delivery status from provider.
    """
    try:
        message = Message.objects.get(provider_message_id=provider_message_id)
        
        if provider == 'whatsapp':
            whatsapp_service = WhatsAppService()
            status = whatsapp_service.get_message_status(provider_message_id)
            
            if status['delivered']:
                message.mark_delivered()
            elif status['read']:
                message.mark_read()
            elif status['failed']:
                message.mark_failed(status['error'])
        
        logger.info(f"Delivery status synced for message {provider_message_id}")
    
    except Message.DoesNotExist:
        logger.error(f"Message with provider ID {provider_message_id} not found")
    except Exception as exc:
        logger.error(f"Error syncing delivery status: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def send_campaign_messages_task(self, campaign_id):
    """
    Send messages for a campaign.
    """
    try:
        campaign = Campaign.objects.get(id=campaign_id)
        
        if campaign.status != 'running':
            logger.warning(f"Campaign {campaign_id} is not running")
            return
        
        # Get contacts from segment
        contacts = Contact.objects.filter(
            tenant=campaign.tenant,
            is_active=True
        )
        
        # Apply segment filters
        if campaign.segment.filter_json:
            from django.db.models import Q
            q = Q()
            
            if 'tags' in campaign.segment.filter_json:
                tags = campaign.segment.filter_json['tags']
                if tags:
                    q &= Q(tags__contains=tags)
            
            if 'attributes' in campaign.segment.filter_json:
                for key, value in campaign.segment.filter_json['attributes'].items():
                    q &= Q(attributes__contains={key: value})
            
            if 'opt_in_status' in campaign.segment.filter_json:
                if campaign.segment.filter_json['opt_in_status'] == 'opted_in':
                    q &= Q(opt_in_at__isnull=False, opt_out_at__isnull=True)
                elif campaign.segment.filter_json['opt_in_status'] == 'opted_out':
                    q &= Q(opt_out_at__isnull=False)
            
            contacts = contacts.filter(q)
        
        # Create messages for each contact
        messages_created = 0
        for contact in contacts:
            # Get or create conversation
            conversation, created = Conversation.objects.get_or_create(
                tenant=campaign.tenant,
                contact=contact
            )
            
            # Create message
            message = Message.objects.create(
                tenant=campaign.tenant,
                conversation=conversation,
                direction='out',
                provider='whatsapp',
                text=campaign.template.body_text,
                template=campaign.template,
                template_variables={}  # TODO: Parse variables from contact attributes
            )
            
            # Queue message for sending
            send_message_task.delay(str(message.id))
            messages_created += 1
        
        # Update campaign statistics
        campaign.sent_count = messages_created
        campaign.save()
        
        # Mark campaign as completed if all messages are queued
        campaign.complete()
        
        logger.info(f"Campaign {campaign_id} processed {messages_created} messages")
    
    except Campaign.DoesNotExist:
        logger.error(f"Campaign {campaign_id} not found")
    except Exception as exc:
        logger.error(f"Error processing campaign {campaign_id}: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def ai_suggest_reply_task(self, conversation_id):
    """
    Generate AI suggestions for a conversation.
    """
    try:
        conversation = Conversation.objects.get(id=conversation_id)
        
        # Get recent messages for context
        recent_messages = conversation.messages.order_by('-created_at')[:15]
        context = []
        
        for msg in recent_messages:
            context.append({
                'direction': msg.direction,
                'text': msg.text,
                'timestamp': msg.created_at.isoformat()
            })
        
        # Get AI suggestions
        ai_service = AIService()
        suggestions = ai_service.suggest_reply(
            tenant_name=conversation.tenant.name,
            context=context
        )
        
        # Update conversation with suggestions
        conversation.ai_suggestions = suggestions
        conversation.save()
        
        logger.info(f"AI suggestions generated for conversation {conversation_id}")
    
    except Conversation.DoesNotExist:
        logger.error(f"Conversation {conversation_id} not found")
    except Exception as exc:
        logger.error(f"Error generating AI suggestions: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def ai_summarize_conversation_task(self, conversation_id):
    """
    Generate AI summary for a conversation.
    """
    try:
        conversation = Conversation.objects.get(id=conversation_id)
        
        # Get all messages for context
        messages = conversation.messages.order_by('created_at')
        context = []
        
        for msg in messages:
            context.append({
                'direction': msg.direction,
                'text': msg.text,
                'timestamp': msg.created_at.isoformat()
            })
        
        # Get AI summary
        ai_service = AIService()
        summary = ai_service.summarize_conversation(context)
        
        # Update conversation with summary
        conversation.ai_summary = summary
        conversation.save()
        
        logger.info(f"AI summary generated for conversation {conversation_id}")
    
    except Conversation.DoesNotExist:
        logger.error(f"Conversation {conversation_id} not found")
    except Exception as exc:
        logger.error(f"Error generating AI summary: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def process_inbound_message_task(self, message_data):
    """
    Process an inbound message from webhook.
    """
    try:
        tenant_id = message_data.get('tenant_id')
        contact_phone = message_data.get('contact_phone')
        text = message_data.get('text', '')
        media_url = message_data.get('media_url')
        
        # Get tenant
        from tenants.models import Tenant
        tenant = Tenant.objects.get(id=tenant_id)
        
        # Get or create contact
        contact, created = Contact.objects.get_or_create(
            tenant=tenant,
            phone_e164=contact_phone,
            defaults={'name': contact_phone}  # Use phone as name if not provided
        )
        
        # Get or create conversation
        conversation, created = Conversation.objects.get_or_create(
            tenant=tenant,
            contact=contact
        )
        
        # Create inbound message
        message = Message.objects.create(
            tenant=tenant,
            conversation=conversation,
            direction='in',
            provider='whatsapp',
            text=text,
            media_url=media_url,
            status='delivered'  # Inbound messages are considered delivered
        )
        
        # Update conversation
        conversation.last_message_at = timezone.now()
        conversation.message_count += 1
        conversation.unread_count += 1
        conversation.save()
        
        # Trigger AI suggestions if flow is active
        active_flows = Flow.objects.filter(tenant=tenant, active=True)
        for flow in active_flows:
            # TODO: Implement flow processing logic
            pass
        
        # Generate AI suggestions
        ai_suggest_reply_task.delay(str(conversation.id))
        
        logger.info(f"Inbound message processed for conversation {conversation.id}")
    
    except Exception as exc:
        logger.error(f"Error processing inbound message: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def cleanup_old_messages_task(self, days=30):
    """
    Clean up old messages to save storage.
    """
    try:
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        
        # Delete old messages (keep recent ones)
        old_messages = Message.objects.filter(created_at__lt=cutoff_date)
        count = old_messages.count()
        old_messages.delete()
        
        logger.info(f"Cleaned up {count} old messages")
    
    except Exception as exc:
        logger.error(f"Error cleaning up old messages: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


# Import SMS tasks
from .tasks_sms import *
