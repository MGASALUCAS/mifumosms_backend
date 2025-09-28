"""
Views for messaging functionality.
"""
from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Sum
from django.db import models
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import FilterSet, CharFilter
from django.db.models import JSONField

from .models import (
    Contact, Segment, Template, Conversation, Message, Attachment,
    Campaign, Flow
)
from .serializers import (
    ContactSerializer, ContactCreateSerializer, ContactBulkImportSerializer,
    SegmentSerializer, SegmentCreateSerializer,
    TemplateSerializer, TemplateCreateSerializer,
    ConversationSerializer, MessageSerializer, MessageCreateSerializer,
    CampaignSerializer, CampaignCreateSerializer,
    FlowSerializer, FlowCreateSerializer,
    ConversationSummarySerializer, AISuggestionsSerializer
)
from core.permissions import IsTenantMember, IsTenantAdmin
from core.rate_limits import check_rate_limit, MESSAGE_RATE_LIMITER
from .tasks import send_message_task, ai_suggest_reply_task, ai_summarize_conversation_task


class ContactFilterSet(FilterSet):
    """Custom filter set for Contact model to handle JSONField filtering."""
    
    class Meta:
        model = Contact
        fields = ['name', 'phone_e164', 'email', 'is_active', 'opt_in_at', 'opt_out_at']
        filter_overrides = {
            JSONField: {
                'filter_class': CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            },
        }


class ContactListCreateView(generics.ListCreateAPIView):
    """List and create contacts."""
    
    permission_classes = [IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ContactFilterSet
    search_fields = ['name', 'phone_e164', 'email']
    ordering_fields = ['name', 'created_at', 'last_contacted_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ContactCreateSerializer
        return ContactSerializer
    
    def get_queryset(self):
        """Filter contacts by tenant."""
        return Contact.objects.filter(tenant=self.request.tenant)
    
    def perform_create(self, serializer):
        """Create contact for the current tenant."""
        serializer.save(tenant=self.request.tenant)


class ContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a contact."""
    
    permission_classes = [IsAuthenticated, IsTenantMember]
    serializer_class = ContactSerializer
    
    def get_queryset(self):
        """Filter contacts by tenant."""
        return Contact.objects.filter(tenant=self.request.tenant)


class ContactBulkImportView(generics.GenericAPIView):
    """Bulk import contacts from CSV."""
    
    permission_classes = [IsAuthenticated, IsTenantMember]
    serializer_class = ContactBulkImportSerializer
    
    def post(self, request, *args, **kwargs):
        """Import contacts from CSV data."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        csv_data = serializer.validated_data['csv_data']
        imported_count = 0
        errors = []
        
        import csv
        from io import StringIO
        
        csv_reader = csv.DictReader(StringIO(csv_data))
        
        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 for header
            try:
                contact_data = {
                    'name': row['name'].strip(),
                    'phone_e164': row['phone_e164'].strip(),
                    'email': row.get('email', '').strip(),
                    'tags': row.get('tags', '').split(',') if row.get('tags') else [],
                    'attributes': {}
                }
                
                # Parse additional attributes
                for key, value in row.items():
                    if key not in ['name', 'phone_e164', 'email', 'tags'] and value.strip():
                        contact_data['attributes'][key] = value.strip()
                
                contact_serializer = ContactCreateSerializer(data=contact_data)
                if contact_serializer.is_valid():
                    contact_serializer.save(tenant=request.tenant)
                    imported_count += 1
                else:
                    errors.append(f"Row {row_num}: {contact_serializer.errors}")
            
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
        return Response({
            'message': f'Imported {imported_count} contacts',
            'imported_count': imported_count,
            'errors': errors
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTenantMember])
def contact_opt_in(request, contact_id):
    """Opt in a contact."""
    contact = get_object_or_404(Contact, id=contact_id, tenant=request.tenant)
    contact.opt_in()
    
    return Response({'message': 'Contact opted in successfully'})


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTenantMember])
def contact_opt_out(request, contact_id):
    """Opt out a contact."""
    contact = get_object_or_404(Contact, id=contact_id, tenant=request.tenant)
    reason = request.data.get('reason', '')
    contact.opt_out(reason)
    
    return Response({'message': 'Contact opted out successfully'})


class SegmentListCreateView(generics.ListCreateAPIView):
    """List and create segments."""
    
    permission_classes = [IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'contact_count']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SegmentCreateSerializer
        return SegmentSerializer
    
    def get_queryset(self):
        """Filter segments by tenant."""
        return Segment.objects.filter(tenant=self.request.tenant)


class SegmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a segment."""
    
    permission_classes = [IsAuthenticated, IsTenantMember]
    serializer_class = SegmentSerializer
    
    def get_queryset(self):
        """Filter segments by tenant."""
        return Segment.objects.filter(tenant=self.request.tenant)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTenantMember])
def segment_update_count(request, segment_id):
    """Update segment contact count."""
    segment = get_object_or_404(Segment, id=segment_id, tenant=request.tenant)
    segment.update_contact_count()
    
    return Response({
        'message': 'Contact count updated',
        'contact_count': segment.contact_count
    })


class TemplateListCreateView(generics.ListCreateAPIView):
    """List and create templates."""
    
    permission_classes = [IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'language', 'approved']
    search_fields = ['name', 'body_text']
    ordering_fields = ['name', 'created_at', 'usage_count']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TemplateCreateSerializer
        return TemplateSerializer
    
    def get_queryset(self):
        """Filter templates by tenant."""
        return Template.objects.filter(tenant=self.request.tenant)


class TemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a template."""
    
    permission_classes = [IsAuthenticated, IsTenantMember]
    serializer_class = TemplateSerializer
    
    def get_queryset(self):
        """Filter templates by tenant."""
        return Template.objects.filter(tenant=self.request.tenant)


class ConversationListCreateView(generics.ListCreateAPIView):
    """List and create conversations."""
    
    permission_classes = [IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['contact__name', 'contact__phone_e164', 'subject']
    ordering_fields = ['created_at', 'last_message_at', 'unread_count']
    ordering = ['-last_message_at', '-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ConversationSerializer
        return ConversationSerializer
    
    def get_queryset(self):
        """Filter conversations by tenant."""
        return Conversation.objects.filter(tenant=self.request.tenant).select_related('contact')


class ConversationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a conversation."""
    
    permission_classes = [IsAuthenticated, IsTenantMember]
    serializer_class = ConversationSerializer
    
    def get_queryset(self):
        """Filter conversations by tenant."""
        return Conversation.objects.filter(tenant=self.request.tenant).select_related('contact')


class MessageListCreateView(generics.ListCreateAPIView):
    """List and create messages."""
    
    permission_classes = [IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['direction', 'provider', 'status', 'conversation']
    search_fields = ['text']
    ordering_fields = ['created_at', 'sent_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MessageCreateSerializer
        return MessageSerializer
    
    def get_queryset(self):
        """Filter messages by tenant."""
        return Message.objects.filter(tenant=self.request.tenant).select_related('conversation__contact')
    
    def perform_create(self, serializer):
        """Create message and trigger sending."""
        message = serializer.save(tenant=self.request.tenant)
        
        # Check rate limits
        check_rate_limit(self.request, MESSAGE_RATE_LIMITER)
        
        # Queue message for sending
        send_message_task.delay(str(message.id))


class MessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a message."""
    
    permission_classes = [IsAuthenticated, IsTenantMember]
    serializer_class = MessageSerializer
    
    def get_queryset(self):
        """Filter messages by tenant."""
        return Message.objects.filter(tenant=self.request.tenant)


class CampaignListCreateView(generics.ListCreateAPIView):
    """List and create campaigns."""
    
    permission_classes = [IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'template', 'segment']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'schedule_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CampaignCreateSerializer
        return CampaignSerializer
    
    def get_queryset(self):
        """Filter campaigns by tenant."""
        return Campaign.objects.filter(tenant=self.request.tenant).select_related('template', 'segment')


class CampaignDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a campaign."""
    
    permission_classes = [IsAuthenticated, IsTenantMember]
    serializer_class = CampaignSerializer
    
    def get_queryset(self):
        """Filter campaigns by tenant."""
        return Campaign.objects.filter(tenant=self.request.tenant)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTenantMember])
def campaign_start(request, campaign_id):
    """Start a campaign."""
    campaign = get_object_or_404(Campaign, id=campaign_id, tenant=request.tenant)
    
    if campaign.status != 'draft':
        return Response({'error': 'Campaign can only be started from draft status'}, status=status.HTTP_400_BAD_REQUEST)
    
    campaign.start()
    
    # Queue campaign messages for sending
    from .tasks import send_campaign_messages_task
    send_campaign_messages_task.delay(str(campaign.id))
    
    return Response({'message': 'Campaign started successfully'})


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTenantMember])
def campaign_pause(request, campaign_id):
    """Pause a campaign."""
    campaign = get_object_or_404(Campaign, id=campaign_id, tenant=request.tenant)
    campaign.pause()
    
    return Response({'message': 'Campaign paused successfully'})


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTenantMember])
def campaign_cancel(request, campaign_id):
    """Cancel a campaign."""
    campaign = get_object_or_404(Campaign, id=campaign_id, tenant=request.tenant)
    campaign.cancel()
    
    return Response({'message': 'Campaign cancelled successfully'})


class FlowListCreateView(generics.ListCreateAPIView):
    """List and create flows."""
    
    permission_classes = [IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'trigger_count']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return FlowCreateSerializer
        return FlowSerializer
    
    def get_queryset(self):
        """Filter flows by tenant."""
        return Flow.objects.filter(tenant=self.request.tenant)


class FlowDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a flow."""
    
    permission_classes = [IsAuthenticated, IsTenantMember]
    serializer_class = FlowSerializer
    
    def get_queryset(self):
        """Filter flows by tenant."""
        return Flow.objects.filter(tenant=self.request.tenant)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTenantMember])
def flow_activate(request, flow_id):
    """Activate a flow."""
    flow = get_object_or_404(Flow, id=flow_id, tenant=request.tenant)
    flow.activate()
    
    return Response({'message': 'Flow activated successfully'})


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTenantMember])
def flow_deactivate(request, flow_id):
    """Deactivate a flow."""
    flow = get_object_or_404(Flow, id=flow_id, tenant=request.tenant)
    flow.deactivate()
    
    return Response({'message': 'Flow deactivated successfully'})


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTenantMember])
def ai_suggest_reply(request, conversation_id):
    """Get AI suggestions for a conversation."""
    conversation = get_object_or_404(Conversation, id=conversation_id, tenant=request.tenant)
    
    # Queue AI task
    ai_suggest_reply_task.delay(str(conversation.id))
    
    return Response({'message': 'AI suggestions requested'})


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTenantMember])
def ai_summarize_conversation(request, conversation_id):
    """Get AI summary for a conversation."""
    conversation = get_object_or_404(Conversation, id=conversation_id, tenant=request.tenant)
    
    # Queue AI task
    ai_summarize_conversation_task.delay(str(conversation.id))
    
    return Response({'message': 'AI summary requested'})


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTenantMember])
def analytics_overview(request):
    """Get analytics overview for the tenant."""
    tenant = request.tenant
    
    # Message statistics
    total_messages = Message.objects.filter(tenant=tenant).count()
    sent_messages = Message.objects.filter(tenant=tenant, direction='out', status__in=['sent', 'delivered', 'read']).count()
    delivered_messages = Message.objects.filter(tenant=tenant, direction='out', status__in=['delivered', 'read']).count()
    read_messages = Message.objects.filter(tenant=tenant, direction='out', status='read').count()
    
    # Conversation statistics
    total_conversations = Conversation.objects.filter(tenant=tenant).count()
    open_conversations = Conversation.objects.filter(tenant=tenant, status='open').count()
    
    # Contact statistics
    total_contacts = Contact.objects.filter(tenant=tenant).count()
    opted_in_contacts = Contact.objects.filter(tenant=tenant, opt_in_at__isnull=False, opt_out_at__isnull=True).count()
    
    # Cost statistics
    total_cost = Message.objects.filter(tenant=tenant).aggregate(
        total=Sum('cost_micro')
    )['total'] or 0
    
    return Response({
        'messages': {
            'total': total_messages,
            'sent': sent_messages,
            'delivered': delivered_messages,
            'read': read_messages,
            'delivery_rate': (delivered_messages / sent_messages * 100) if sent_messages > 0 else 0,
            'read_rate': (read_messages / delivered_messages * 100) if delivered_messages > 0 else 0,
        },
        'conversations': {
            'total': total_conversations,
            'open': open_conversations,
        },
        'contacts': {
            'total': total_contacts,
            'opted_in': opted_in_contacts,
            'opt_in_rate': (opted_in_contacts / total_contacts * 100) if total_contacts > 0 else 0,
        },
        'cost': {
            'total_dollars': total_cost / 1000000,
            'total_micro': total_cost,
        }
    })
