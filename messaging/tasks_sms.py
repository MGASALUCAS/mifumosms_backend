"""
SMS-specific Celery tasks for Mifumo WMS.
"""
import logging
from celery import shared_task
from django.utils import timezone
from django.db import transaction

from .models_sms import SMSMessage, SMSDeliveryReport, SMSBulkUpload
from .services.sms_service import SMSService, SMSBulkProcessor

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_sms_task(self, message_id, sender_id, provider_id=None):
    """
    Send SMS message asynchronously.
    
    Args:
        message_id: ID of the base message
        sender_id: Sender ID to use
        provider_id: Optional provider ID
    """
    try:
        from .models import Message
        from .services.sms_validation import SMSValidationService, SMSValidationError
        
        # Get base message
        base_message = Message.objects.get(id=message_id)
        
        # Initialize SMS validation service
        validation_service = SMSValidationService(base_message.tenant)
        
        # Validate SMS sending capability
        validation_result = validation_service.validate_sms_sending(sender_id, required_credits=1)
        
        if not validation_result['valid']:
            # Mark message as failed with validation error
            base_message.status = 'failed'
            base_message.error_message = validation_result['error']
            base_message.save()
            
            logger.error(f"SMS validation failed for message {message_id}: {validation_result['error']}")
            return
        
        # Get SMS provider and sender ID
        from .models_sms import SMSProvider, SMSSenderID
        
        provider = SMSProvider.objects.filter(
            tenant=base_message.tenant,
            is_active=True,
            is_default=True
        ).first()
        
        if not provider:
            provider = SMSProvider.objects.filter(
                tenant=base_message.tenant,
                is_active=True
            ).first()
        
        if not provider:
            raise Exception("No active SMS provider found")
        
        sms_sender_id = SMSSenderID.objects.filter(
            tenant=base_message.tenant,
            sender_id=sender_id,
            status='active'
        ).first()
        
        if not sms_sender_id:
            raise Exception(f"Sender ID '{sender_id}' not found or not active")
        
        # Create SMS message record
        sms_message = SMSMessage.objects.create(
            tenant=base_message.tenant,
            base_message=base_message,
            provider=provider,
            sender_id=sms_sender_id,
            cost_amount=provider.cost_per_sms,
            cost_currency=provider.currency
        )
        
        # Send SMS
        sms_service = SMSService(str(base_message.tenant.id))
        
        # Get phone number from contact
        phone = base_message.conversation.contact.phone_e164
        if phone.startswith('+'):
            phone = phone[1:]
        
        result = sms_service.send_sms(
            to=phone,
            message=base_message.text,
            sender_id=sender_id,
            recipient_id=str(base_message.id)
        )
        
        if result['success']:
            # Deduct SMS credits after successful send
            try:
                validation_service.deduct_credits(
                    amount=1,
                    sender_id=sender_id,
                    message_id=str(base_message.id),
                    description=f"SMS sent to {phone}"
                )
                logger.info(f"Deducted 1 SMS credit for message {message_id}")
            except SMSValidationError as e:
                logger.error(f"Failed to deduct credits for message {message_id}: {e}")
                # Don't fail the message if credit deduction fails, just log it
            
            # Update SMS message
            sms_message.status = 'sent'
            sms_message.provider_message_id = result.get('message_id')
            sms_message.provider_request_id = result.get('request_id')
            sms_message.provider_response = result.get('response', {})
            sms_message.sent_at = timezone.now()
            sms_message.save()
            
            # Update base message
            base_message.status = 'sent'
            base_message.provider_message_id = result.get('message_id')
            base_message.sent_at = timezone.now()
            base_message.save()
            
            # Schedule delivery report check
            check_sms_delivery_task.apply_async(
                args=[str(sms_message.id)],
                countdown=300  # Check after 5 minutes
            )
            
            logger.info(f"SMS sent successfully: {message_id}")
            
        else:
            # Update with error
            sms_message.status = 'failed'
            sms_message.error_code = result.get('error_code')
            sms_message.error_message = result.get('error')
            sms_message.failed_at = timezone.now()
            sms_message.save()
            
            base_message.status = 'failed'
            base_message.error_message = result.get('error')
            base_message.save()
            
            logger.error(f"SMS send failed: {message_id} - {result.get('error')}")
            
    except Exception as exc:
        logger.error(f"SMS send task failed: {str(exc)}")
        
        # Update message status
        try:
            from .models import Message
            base_message = Message.objects.get(id=message_id)
            base_message.status = 'failed'
            base_message.error_message = str(exc)
            base_message.save()
        except:
            pass
        
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def check_sms_delivery_task(self, sms_message_id):
    """
    Check SMS delivery status.
    
    Args:
        sms_message_id: ID of the SMS message
    """
    try:
        sms_message = SMSMessage.objects.get(id=sms_message_id)
        
        if not sms_message.provider_request_id:
            logger.warning(f"No provider request ID for SMS message: {sms_message_id}")
            return
        
        # Get phone number
        phone = sms_message.base_message.conversation.contact.phone_e164
        if phone.startswith('+'):
            phone = phone[1:]
        
        # Check delivery status
        sms_service = SMSService(str(sms_message.tenant.id))
        result = sms_service.get_delivery_report(
            sms_message.provider_request_id,
            phone
        )
        
        if result['success']:
            reports = result.get('reports', [])
            
            for report_data in reports:
                # Create or update delivery report
                delivery_report, created = SMSDeliveryReport.objects.get_or_create(
                    tenant=sms_message.tenant,
                    sms_message=sms_message,
                    provider_request_id=sms_message.provider_request_id,
                    dest_addr=report_data.get('dest_addr'),
                    defaults={
                        'provider_message_id': report_data.get('request_id'),
                        'status': report_data.get('status', 'pending').lower(),
                        'provider_response': report_data
                    }
                )
                
                if not created:
                    delivery_report.status = report_data.get('status', 'pending').lower()
                    delivery_report.provider_response = report_data
                    delivery_report.save()
                
                # Update SMS message status
                if report_data.get('status') == 'DELIVERED':
                    sms_message.status = 'delivered'
                    sms_message.delivered_at = timezone.now()
                    sms_message.save()
                    
                    # Update base message
                    sms_message.base_message.status = 'delivered'
                    sms_message.base_message.delivered_at = timezone.now()
                    sms_message.base_message.save()
                    
                elif report_data.get('status') == 'UNDELIVERED':
                    sms_message.status = 'undelivered'
                    sms_message.failed_at = timezone.now()
                    sms_message.save()
                    
                    # Update base message
                    sms_message.base_message.status = 'failed'
                    sms_message.base_message.error_message = 'Message undelivered'
                    sms_message.base_message.save()
            
            logger.info(f"Delivery report checked for SMS: {sms_message_id}")
            
        else:
            logger.error(f"Delivery report check failed: {result.get('error')}")
            
    except Exception as exc:
        logger.error(f"Delivery check task failed: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def process_sms_bulk_upload_task(self, upload_id):
    """
    Process bulk SMS upload from Excel file.
    
    Args:
        upload_id: ID of the SMS bulk upload
    """
    try:
        bulk_upload = SMSBulkUpload.objects.get(id=upload_id)
        bulk_upload.status = 'processing'
        bulk_upload.save()
        
        # Process Excel file
        processor = SMSBulkProcessor(str(bulk_upload.tenant.id))
        result = processor.process_excel_upload(
            bulk_upload.file_path,
            str(bulk_upload.campaign_id) if bulk_upload.campaign_id else None
        )
        
        if result['success']:
            # Update bulk upload
            bulk_upload.status = 'completed'
            bulk_upload.total_rows = result['total_rows']
            bulk_upload.processed_rows = result['processed_rows']
            bulk_upload.successful_rows = result['successful_rows']
            bulk_upload.failed_rows = result['failed_rows']
            bulk_upload.errors = result['errors']
            bulk_upload.completed_at = timezone.now()
            bulk_upload.save()
            
            logger.info(f"Bulk SMS upload processed: {upload_id}")
            
        else:
            bulk_upload.status = 'failed'
            bulk_upload.errors = [result['error']]
            bulk_upload.completed_at = timezone.now()
            bulk_upload.save()
            
            logger.error(f"Bulk SMS upload failed: {result['error']}")
            
    except Exception as exc:
        logger.error(f"Bulk upload task failed: {str(exc)}")
        
        try:
            bulk_upload = SMSBulkUpload.objects.get(id=upload_id)
            bulk_upload.status = 'failed'
            bulk_upload.errors = [str(exc)]
            bulk_upload.completed_at = timezone.now()
            bulk_upload.save()
        except:
            pass
        
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def sync_sms_provider_data_task(self, provider_id):
    """
    Sync data from SMS provider (sender IDs, templates, etc.).
    
    Args:
        provider_id: ID of the SMS provider
    """
    try:
        from .models_sms import SMSProvider, SMSSenderID, SMSTemplate
        
        provider = SMSProvider.objects.get(id=provider_id)
        sms_service = SMSService(str(provider.tenant.id))
        
        # Sync sender IDs
        sender_result = sms_service.get_sender_ids()
        if sender_result['success']:
            for sender_data in sender_result['sender_ids']:
                SMSSenderID.objects.update_or_create(
                    tenant=provider.tenant,
                    provider=provider,
                    sender_id=sender_data['senderid'],
                    defaults={
                        'sample_content': sender_data.get('sample_content', ''),
                        'status': sender_data.get('status', 'pending'),
                        'provider_sender_id': sender_data.get('id'),
                        'provider_data': sender_data
                    }
                )
        
        # Sync templates
        template_result = sms_service.get_templates()
        if template_result['success']:
            for template_data in template_result['templates']:
                SMSTemplate.objects.update_or_create(
                    tenant=provider.tenant,
                    provider_template_id=template_data['id'],
                    defaults={
                        'name': template_data['sms_title'],
                        'message': template_data['message'],
                        'provider_data': template_data
                    }
                )
        
        logger.info(f"SMS provider data synced: {provider_id}")
        
    except Exception as exc:
        logger.error(f"Provider sync task failed: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def process_sms_schedule_task(self, schedule_id):
    """
    Process scheduled SMS campaign.
    
    Args:
        schedule_id: ID of the SMS schedule
    """
    try:
        from .models_sms import SMSSchedule
        from .models import Campaign
        
        schedule = SMSSchedule.objects.get(id=schedule_id)
        
        if not schedule.is_active:
            logger.info(f"SMS schedule is inactive: {schedule_id}")
            return
        
        if schedule.next_run and schedule.next_run > timezone.now():
            logger.info(f"SMS schedule not ready: {schedule_id}")
            return
        
        # Get campaign
        campaign = schedule.campaign
        
        if campaign.status not in ['draft', 'scheduled']:
            logger.info(f"Campaign not ready for sending: {campaign.id}")
            return
        
        # Start campaign if it's a draft
        if campaign.status == 'draft':
            campaign.status = 'running'
            campaign.started_at = timezone.now()
            campaign.save()
        
        # Process campaign messages
        from .tasks import send_campaign_messages_task
        send_campaign_messages_task.delay(str(campaign.id))
        
        # Update schedule
        schedule.last_run = timezone.now()
        
        # Calculate next run
        if schedule.frequency == 'once':
            schedule.is_active = False
        elif schedule.frequency == 'daily':
            schedule.next_run = timezone.now() + timezone.timedelta(days=1)
        elif schedule.frequency == 'weekly':
            schedule.next_run = timezone.now() + timezone.timedelta(weeks=1)
        elif schedule.frequency == 'monthly':
            schedule.next_run = timezone.now() + timezone.timedelta(days=30)
        
        schedule.save()
        
        logger.info(f"SMS schedule processed: {schedule_id}")
        
    except Exception as exc:
        logger.error(f"Schedule task failed: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def cleanup_old_sms_data_task(self, days=30):
    """
    Clean up old SMS data to maintain performance.
    
    Args:
        days: Number of days to keep data
    """
    try:
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Clean up old delivery reports
        old_reports = SMSDeliveryReport.objects.filter(
            received_at__lt=cutoff_date
        )
        deleted_reports = old_reports.count()
        old_reports.delete()
        
        # Clean up old bulk uploads
        old_uploads = SMSBulkUpload.objects.filter(
            created_at__lt=cutoff_date,
            status__in=['completed', 'failed']
        )
        deleted_uploads = old_uploads.count()
        old_uploads.delete()
        
        logger.info(f"SMS cleanup completed: {deleted_reports} reports, {deleted_uploads} uploads")
        
    except Exception as exc:
        logger.error(f"Cleanup task failed: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
