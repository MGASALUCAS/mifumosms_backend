"""
SMS-specific API views for Mifumo WMS.
"""
import logging
import pandas as pd
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db import transaction
from django.core.files.storage import default_storage
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from core.permissions import IsTenantMember
from .models_sms import (
    SMSProvider, SMSSenderID, SMSTemplate, SMSMessage,
    SMSDeliveryReport, SMSBulkUpload, SMSSchedule
)
from .serializers_sms import (
    SMSProviderSerializer, SMSSenderIDSerializer, SMSTemplateSerializer,
    SMSMessageSerializer, SMSDeliveryReportSerializer, SMSBulkUploadSerializer,
    SMSScheduleSerializer, SMSBulkSendSerializer, SMSExcelUploadSerializer,
    SMSBalanceSerializer, SMSStatsSerializer
)
from .services.sms_service import SMSService, SMSBulkProcessor
from .tasks import send_sms_task, process_sms_bulk_upload_task

logger = logging.getLogger(__name__)


class SMSProviderListCreateView(generics.ListCreateAPIView):
    """List and create SMS providers."""

    serializer_class = SMSProviderSerializer
    permission_classes = [IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['provider_type', 'is_active', 'is_default']
    search_fields = ['name']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']

    def get_queryset(self):
        return SMSProvider.objects.filter(tenant=self.request.tenant)

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.tenant, created_by=self.request.user)


class SMSProviderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete SMS provider."""

    serializer_class = SMSProviderSerializer
    permission_classes = [IsAuthenticated, IsTenantMember]

    def get_queryset(self):
        return SMSProvider.objects.filter(tenant=self.request.tenant)


class SMSSenderIDListCreateView(generics.ListCreateAPIView):
    """List and create SMS sender IDs."""

    serializer_class = SMSSenderIDSerializer
    permission_classes = [IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'provider']
    search_fields = ['sender_id']
    ordering_fields = ['created_at', 'sender_id']
    ordering = ['-created_at']

    def get_queryset(self):
        return SMSSenderID.objects.filter(tenant=self.request.tenant).select_related('provider')

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.tenant, created_by=self.request.user)


class SMSSenderIDDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete SMS sender ID."""

    serializer_class = SMSSenderIDSerializer
    permission_classes = [IsAuthenticated, IsTenantMember]

    def get_queryset(self):
        return SMSSenderID.objects.filter(tenant=self.request.tenant)


class SMSTemplateListCreateView(generics.ListCreateAPIView):
    """List and create SMS templates."""

    serializer_class = SMSTemplateSerializer
    permission_classes = [IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'language', 'is_active', 'approval_status']
    search_fields = ['name', 'message']
    ordering_fields = ['created_at', 'name', 'usage_count']
    ordering = ['-created_at']

    def get_queryset(self):
        return SMSTemplate.objects.filter(tenant=self.request.tenant)

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.tenant, created_by=self.request.user)


class SMSTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete SMS template."""

    serializer_class = SMSTemplateSerializer
    permission_classes = [IsAuthenticated, IsTenantMember]

    def get_queryset(self):
        return SMSTemplate.objects.filter(tenant=self.request.tenant)


class SMSMessageListView(generics.ListAPIView):
    """List SMS messages."""

    serializer_class = SMSMessageSerializer
    permission_classes = [IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'provider', 'sender_id', 'template']
    search_fields = ['provider_message_id', 'base_message__conversation__contact__name']
    ordering_fields = ['created_at', 'sent_at', 'delivered_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return SMSMessage.objects.filter(tenant=self.request.tenant).select_related(
            'provider', 'sender_id', 'template', 'base_message__conversation__contact'
        )


class SMSDeliveryReportListView(generics.ListAPIView):
    """List SMS delivery reports."""

    serializer_class = SMSDeliveryReportSerializer
    permission_classes = [IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'sms_message']
    search_fields = ['dest_addr', 'provider_message_id']
    ordering_fields = ['received_at', 'delivered_at']
    ordering = ['-received_at']

    def get_queryset(self):
        return SMSDeliveryReport.objects.filter(tenant=self.request.tenant)


class SMSBulkUploadListView(generics.ListAPIView):
    """List SMS bulk uploads."""

    serializer_class = SMSBulkUploadSerializer
    permission_classes = [IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'campaign']
    search_fields = ['file_name']
    ordering_fields = ['created_at', 'completed_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return SMSBulkUpload.objects.filter(tenant=self.request.tenant).select_related('campaign')


class SMSScheduleListCreateView(generics.ListCreateAPIView):
    """List and create SMS schedules."""

    serializer_class = SMSScheduleSerializer
    permission_classes = [IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['frequency', 'is_active', 'campaign']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'start_date', 'next_run']
    ordering = ['-created_at']

    def get_queryset(self):
        return SMSSchedule.objects.filter(tenant=self.request.tenant).select_related('campaign')

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.tenant, created_by=self.request.user)


class SMSScheduleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete SMS schedule."""

    serializer_class = SMSScheduleSerializer
    permission_classes = [IsAuthenticated, IsTenantMember]

    def get_queryset(self):
        return SMSSchedule.objects.filter(tenant=self.request.tenant)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTenantMember])
def send_sms_view(request):
    """Send SMS message."""
    try:
        # Get or create contact
        phone = request.data.get('phone')
        message = request.data.get('message')
        sender_id = request.data.get('sender_id')

        if not all([phone, message, sender_id]):
            return Response(
                {'error': 'Phone, message, and sender_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get or create contact
        from .models import Contact, Conversation
        contact, created = Contact.objects.get_or_create(
            tenant=request.tenant,
            phone_e164=phone,
            defaults={'name': phone}
        )

        # Get or create conversation
        conversation, created = Conversation.objects.get_or_create(
            tenant=request.tenant,
            contact=contact
        )

        # Create base message
        from .models import Message
        message_obj = Message.objects.create(
            tenant=request.tenant,
            conversation=conversation,
            direction='out',
            provider='sms',
            text=message,
            recipient_number=phone
        )

        # Send SMS asynchronously
        send_sms_task.delay(str(message_obj.id), sender_id)

        return Response({
            'success': True,
            'message_id': str(message_obj.id),
            'message': 'SMS queued for sending'
        })

    except Exception as e:
        logger.error(f"SMS send error: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTenantMember])
def send_bulk_sms_view(request):
    """Send bulk SMS messages."""
    try:
        serializer = SMSBulkSendSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        contacts = data['contacts']
        message = data['message']
        sender_id = data['sender_id']
        template_id = data.get('template_id')
        schedule_at = data.get('schedule_at')
        campaign_id = data.get('campaign_id')

        # Create campaign if provided
        campaign = None
        if campaign_id:
            from .models import Campaign
            campaign = Campaign.objects.get(id=campaign_id, tenant=request.tenant)

        # Process each contact
        results = []
        for i, contact_data in enumerate(contacts):
            try:
                phone = contact_data['phone']
                if phone.startswith('+'):
                    phone = phone[1:]

                # Get or create contact
                from .models import Contact, Conversation
                contact, created = Contact.objects.get_or_create(
                    tenant=request.tenant,
                    phone_e164=phone,
                    defaults={'name': contact_data.get('name', phone)}
                )

                # Get or create conversation
                conversation, created = Conversation.objects.get_or_create(
                    tenant=request.tenant,
                    contact=contact
                )

                # Create base message
                from .models import Message
                message_obj = Message.objects.create(
                    tenant=request.tenant,
                    conversation=conversation,
                    direction='out',
                    provider='sms',
                    text=message,
                    recipient_number=phone
                )

                # Send SMS asynchronously
                send_sms_task.delay(str(message_obj.id), sender_id)

                results.append({
                    'phone': phone,
                    'success': True,
                    'message_id': str(message_obj.id)
                })

            except Exception as e:
                results.append({
                    'phone': contact_data.get('phone', 'unknown'),
                    'success': False,
                    'error': str(e)
                })

        return Response({
            'success': True,
            'total_contacts': len(contacts),
            'processed_contacts': len(results),
            'successful_contacts': len([r for r in results if r['success']]),
            'results': results
        })

    except Exception as e:
        logger.error(f"Bulk SMS send error: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTenantMember])
def upload_excel_sms_view(request):
    """Upload Excel file for bulk SMS sending."""
    try:
        serializer = SMSExcelUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        file = data['file']
        campaign_id = data.get('campaign_id')
        template_id = data.get('template_id')
        sender_id = data.get('sender_id')

        # Save file
        file_path = default_storage.save(f'sms_uploads/{file.name}', file)

        # Create bulk upload record
        bulk_upload = SMSBulkUpload.objects.create(
            tenant=request.tenant,
            file_name=file.name,
            file_path=file_path,
            file_size=file.size,
            campaign_id=campaign_id,
            created_by=request.user
        )

        # Process file asynchronously
        process_sms_bulk_upload_task.delay(str(bulk_upload.id))

        return Response({
            'success': True,
            'upload_id': str(bulk_upload.id),
            'message': 'File uploaded and queued for processing'
        })

    except Exception as e:
        logger.error(f"Excel upload error: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTenantMember])
def sms_balance_view(request):
    """Get SMS account balance."""
    try:
        provider_id = request.query_params.get('provider_id')
        sms_service = SMSService(str(request.tenant.id))

        result = sms_service.check_balance(provider_id)

        if result['success']:
            return Response({
                'success': True,
                'balance': result['balance'],
                'currency': 'USD',  # Default currency
                'provider': 'Beem Africa'
            })
        else:
            return Response(
                {'error': result['error']},
                status=status.HTTP_400_BAD_REQUEST
            )

    except Exception as e:
        logger.error(f"Balance check error: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTenantMember])
def sms_stats_view(request):
    """Get SMS statistics."""
    try:
        from django.db.models import Count, Sum, Avg
        from django.utils import timezone
        from datetime import timedelta

        # Get date range
        days = int(request.query_params.get('days', 30))
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        # Get statistics
        messages = SMSMessage.objects.filter(
            tenant=request.tenant,
            created_at__range=[start_date, end_date]
        )

        total_sent = messages.count()
        total_delivered = messages.filter(status='delivered').count()
        total_failed = messages.filter(status='failed').count()
        delivery_rate = (total_delivered / total_sent * 100) if total_sent > 0 else 0

        # Get total cost
        cost_data = messages.aggregate(
            total_cost=Sum('cost_amount')
        )
        total_cost = cost_data['total_cost'] or 0

        return Response({
            'success': True,
            'total_sent': total_sent,
            'total_delivered': total_delivered,
            'total_failed': total_failed,
            'delivery_rate': round(delivery_rate, 2),
            'total_cost': float(total_cost),
            'currency': 'USD',
            'period_start': start_date,
            'period_end': end_date
        })

    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTenantMember])
def create_sender_id_view(request):
    """Create SMS sender ID."""
    try:
        sender_id = request.data.get('sender_id')
        sample_content = request.data.get('sample_content')

        if not all([sender_id, sample_content]):
            return Response(
                {'error': 'sender_id and sample_content are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        sms_service = SMSService(str(request.tenant.id))
        result = sms_service.create_sender_id(sender_id, sample_content)

        if result['success']:
            # Save to database
            provider = SMSProvider.objects.filter(
                tenant=request.tenant,
                is_active=True,
                is_default=True
            ).first()

            if provider:
                sms_sender_id = SMSSenderID.objects.create(
                    tenant=request.tenant,
                    provider=provider,
                    sender_id=sender_id,
                    sample_content=sample_content,
                    status='pending',
                    provider_sender_id=result.get('id'),
                    created_by=request.user
                )

                return Response({
                    'success': True,
                    'sender_id': SMSSenderIDSerializer(sms_sender_id).data,
                    'message': 'Sender ID created successfully'
                })
            else:
                return Response(
                    {'error': 'No active SMS provider found'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {'error': result['error']},
                status=status.HTTP_400_BAD_REQUEST
            )

    except Exception as e:
        logger.error(f"Sender ID creation error: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTenantMember])
def create_sms_template_view(request):
    """Create SMS template."""
    try:
        name = request.data.get('name')
        message = request.data.get('message')
        category = request.data.get('category', 'PROMOTIONAL')

        if not all([name, message]):
            return Response(
                {'error': 'name and message are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        sms_service = SMSService(str(request.tenant.id))
        result = sms_service.create_template(name, message)

        if result['success']:
            # Save to database
            sms_template = SMSTemplate.objects.create(
                tenant=request.tenant,
                name=name,
                category=category,
                message=message,
                provider_template_id=result.get('template_id'),
                created_by=request.user
            )

            return Response({
                'success': True,
                'template': SMSTemplateSerializer(sms_template).data,
                'message': 'Template created successfully'
            })
        else:
            return Response(
                {'error': result['error']},
                status=status.HTTP_400_BAD_REQUEST
            )

    except Exception as e:
        logger.error(f"Template creation error: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
