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
    ConversationSummarySerializer, AISuggestionsSerializer,
    PurchaseHistorySerializer, PurchaseHistorySummarySerializer
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

    permission_classes = [IsAuthenticated]
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
        """Filter contacts by user."""
        return Contact.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        """Create contact for the current user."""
        serializer.save(created_by=self.request.user)


class ContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a contact."""

    permission_classes = [IsAuthenticated]
    serializer_class = ContactSerializer

    def get_queryset(self):
        """Filter contacts by user."""
        return Contact.objects.filter(created_by=self.request.user)


class ContactBulkImportView(generics.GenericAPIView):
    """Bulk import contacts from CSV."""

    permission_classes = [IsAuthenticated]
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
                    contact_serializer.save(created_by=request.user)
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
@permission_classes([IsAuthenticated])
def contact_opt_in(request, contact_id):
    """Opt in a contact."""
    contact = get_object_or_404(Contact, id=contact_id, created_by=request.user)
    contact.opt_in()

    return Response({'message': 'Contact opted in successfully'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def contact_opt_out(request, contact_id):
    """Opt out a contact."""
    contact = get_object_or_404(Contact, id=contact_id, created_by=request.user)
    reason = request.data.get('reason', '')
    contact.opt_out(reason)

    return Response({'message': 'Contact opted out successfully'})


class SegmentListCreateView(generics.ListCreateAPIView):
    """List and create segments."""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'contact_count']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SegmentCreateSerializer
        return SegmentSerializer

    def get_queryset(self):
        """Filter segments by user."""
        return Segment.objects.filter(created_by=self.request.user)


class SegmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a segment."""

    permission_classes = [IsAuthenticated]
    serializer_class = SegmentSerializer

    def get_queryset(self):
        """Filter segments by user."""
        return Segment.objects.filter(created_by=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def segment_update_count(request, segment_id):
    """Update segment contact count."""
    segment = get_object_or_404(Segment, id=segment_id, created_by=request.user)
    segment.update_contact_count()

    return Response({
        'message': 'Contact count updated',
        'contact_count': segment.contact_count
    })


class TemplateListCreateView(generics.ListCreateAPIView):
    """List and create templates."""

    permission_classes = [IsAuthenticated]
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
        """Filter templates by user."""
        return Template.objects.filter(created_by=self.request.user)


class TemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a template."""

    permission_classes = [IsAuthenticated]
    serializer_class = TemplateSerializer

    def get_queryset(self):
        """Filter templates by user."""
        return Template.objects.filter(created_by=self.request.user)


class ConversationListCreateView(generics.ListCreateAPIView):
    """List and create conversations."""

    permission_classes = [IsAuthenticated]
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
        """Filter conversations by user."""
        return Conversation.objects.filter(contact__created_by=self.request.user).select_related('contact')


class ConversationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a conversation."""

    permission_classes = [IsAuthenticated]
    serializer_class = ConversationSerializer

    def get_queryset(self):
        """Filter conversations by user."""
        return Conversation.objects.filter(contact__created_by=self.request.user).select_related('contact')


class MessageListCreateView(generics.ListCreateAPIView):
    """List and create messages."""

    permission_classes = [IsAuthenticated]
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
        """Filter messages by user."""
        return Message.objects.filter(conversation__contact__created_by=self.request.user).select_related('conversation__contact')

    def perform_create(self, serializer):
        """Create message and trigger sending."""
        message = serializer.save()

        # Check rate limits
        check_rate_limit(self.request, MESSAGE_RATE_LIMITER)

        # Queue message for sending
        send_message_task.delay(str(message.id))


class MessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a message."""

    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def get_queryset(self):
        """Filter messages by user."""
        return Message.objects.filter(conversation__contact__created_by=self.request.user)


class CampaignListCreateView(generics.ListCreateAPIView):
    """List and create campaigns."""

    permission_classes = [IsAuthenticated]
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
        """Filter campaigns by user."""
        return Campaign.objects.filter(created_by=self.request.user).select_related('template', 'segment')


class CampaignDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a campaign."""

    permission_classes = [IsAuthenticated]
    serializer_class = CampaignSerializer

    def get_queryset(self):
        """Filter campaigns by user."""
        return Campaign.objects.filter(created_by=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def campaign_start(request, campaign_id):
    """Start a campaign."""
    campaign = get_object_or_404(Campaign, id=campaign_id, created_by=request.user)

    if campaign.status != 'draft':
        return Response({'error': 'Campaign can only be started from draft status'}, status=status.HTTP_400_BAD_REQUEST)

    campaign.start()

    # Queue campaign messages for sending
    from .tasks import send_campaign_messages_task
    send_campaign_messages_task.delay(str(campaign.id))

    return Response({'message': 'Campaign started successfully'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def campaign_pause(request, campaign_id):
    """Pause a campaign."""
    campaign = get_object_or_404(Campaign, id=campaign_id, created_by=request.user)
    campaign.pause()

    return Response({'message': 'Campaign paused successfully'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def campaign_cancel(request, campaign_id):
    """Cancel a campaign."""
    campaign = get_object_or_404(Campaign, id=campaign_id, created_by=request.user)
    campaign.cancel()

    return Response({'message': 'Campaign cancelled successfully'})


class FlowListCreateView(generics.ListCreateAPIView):
    """List and create flows."""

    permission_classes = [IsAuthenticated]
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
        """Filter flows by user."""
        return Flow.objects.filter(created_by=self.request.user)


class FlowDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a flow."""

    permission_classes = [IsAuthenticated]
    serializer_class = FlowSerializer

    def get_queryset(self):
        """Filter flows by user."""
        return Flow.objects.filter(created_by=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def flow_activate(request, flow_id):
    """Activate a flow."""
    flow = get_object_or_404(Flow, id=flow_id, created_by=request.user)
    flow.activate()

    return Response({'message': 'Flow activated successfully'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def flow_deactivate(request, flow_id):
    """Deactivate a flow."""
    flow = get_object_or_404(Flow, id=flow_id, created_by=request.user)
    flow.deactivate()

    return Response({'message': 'Flow deactivated successfully'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_suggest_reply(request, conversation_id):
    """Get AI suggestions for a conversation."""
    conversation = get_object_or_404(Conversation, id=conversation_id, contact__created_by=request.user)

    # Queue AI task
    ai_suggest_reply_task.delay(str(conversation.id))

    return Response({'message': 'AI suggestions requested'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_summarize_conversation(request, conversation_id):
    """Get AI summary for a conversation."""
    conversation = get_object_or_404(Conversation, id=conversation_id, contact__created_by=request.user)

    # Queue AI task
    ai_summarize_conversation_task.delay(str(conversation.id))

    return Response({'message': 'AI summary requested'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_overview(request):
    """Get analytics overview for the user."""
    user = request.user

    # Message statistics
    total_messages = Message.objects.filter(conversation__contact__created_by=user).count()
    sent_messages = Message.objects.filter(conversation__contact__created_by=user, direction='out', status__in=['sent', 'delivered', 'read']).count()
    delivered_messages = Message.objects.filter(conversation__contact__created_by=user, direction='out', status__in=['delivered', 'read']).count()
    read_messages = Message.objects.filter(conversation__contact__created_by=user, direction='out', status='read').count()

    # Conversation statistics
    total_conversations = Conversation.objects.filter(contact__created_by=user).count()
    open_conversations = Conversation.objects.filter(contact__created_by=user, status='open').count()

    # Contact statistics
    total_contacts = Contact.objects.filter(created_by=user).count()
    opted_in_contacts = Contact.objects.filter(created_by=user, opt_in_at__isnull=False, opt_out_at__isnull=True).count()

    # Cost statistics
    total_cost = Message.objects.filter(conversation__contact__created_by=user).aggregate(
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


# =============================================
# PURCHASE HISTORY VIEWS
# =============================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def purchase_history(request):
    """
    Get purchase history for the authenticated user.
    GET /api/messaging/purchase-history/
    
    Query Parameters:
    - status: Filter by purchase status (pending, completed, failed, cancelled, refunded)
    - start_date: Filter from date (YYYY-MM-DD)
    - end_date: Filter to date (YYYY-MM-DD)
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20)
    - search: Search in invoice number or package name
    """
    try:
        from billing.models import Purchase
        from django.core.paginator import Paginator
        from django.db.models import Q, Count, Sum, Avg
        from datetime import datetime
        
        # Get query parameters
        status_filter = request.GET.get('status')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        search = request.GET.get('search', '').strip()
        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('page_size', 20)), 100)  # Max 100 items per page
        
        # Build queryset - filter by user
        queryset = Purchase.objects.filter(user=request.user).select_related('package')
        
        # Apply filters
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__gte=start_dt)
            except ValueError:
                return Response({
                    'success': False,
                    'message': 'Invalid start_date format. Use YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__lte=end_dt)
            except ValueError:
                return Response({
                    'success': False,
                    'message': 'Invalid end_date format. Use YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        if search:
            queryset = queryset.filter(
                Q(invoice_number__icontains=search) |
                Q(package__name__icontains=search)
            )
        
        # Order by creation date (newest first)
        queryset = queryset.order_by('-created_at')
        
        # Pagination
        paginator = Paginator(queryset, page_size)
        total_count = paginator.count
        
        try:
            purchases_page = paginator.page(page)
        except:
            return Response({
                'success': False,
                'message': f'Invalid page number. Available pages: 1-{paginator.num_pages}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Serialize purchase data
        purchase_data = []
        for purchase in purchases_page:
            purchase_data.append({
                'id': str(purchase.id),
                'invoice_number': purchase.invoice_number,
                'package_name': purchase.package.name,
                'package_type': purchase.package.package_type,
                'credits': purchase.credits,
                'amount': float(purchase.amount),
                'unit_price': float(purchase.unit_price),
                'payment_method': purchase.payment_method,
                'payment_method_display': purchase.get_payment_method_display(),
                'payment_reference': purchase.payment_reference,
                'status': purchase.status,
                'status_display': purchase.get_status_display(),
                'created_at': purchase.created_at.isoformat(),
                'completed_at': purchase.completed_at.isoformat() if purchase.completed_at else None,
                'updated_at': purchase.updated_at.isoformat()
            })
        
        return Response({
            'success': True,
            'data': {
                'purchases': purchase_data,
                'pagination': {
                    'page': page,
                    'page_size': page_size,
                    'total_count': total_count,
                    'total_pages': paginator.num_pages,
                    'has_next': purchases_page.has_next(),
                    'has_previous': purchases_page.has_previous(),
                    'next_page': purchases_page.next_page_number() if purchases_page.has_next() else None,
                    'previous_page': purchases_page.previous_page_number() if purchases_page.has_previous() else None
                }
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': 'Failed to retrieve purchase history',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def purchase_history_summary(request):
    """
    Get purchase history summary statistics for the authenticated user.
    GET /api/messaging/purchase-history/summary/
    
    Query Parameters:
    - start_date: Filter from date (YYYY-MM-DD)
    - end_date: Filter to date (YYYY-MM-DD)
    """
    try:
        from billing.models import Purchase
        from django.db.models import Count, Sum, Avg, Max
        from datetime import datetime
        
        # Get query parameters
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        # Build queryset - filter by user
        queryset = Purchase.objects.filter(user=request.user)
        
        # Apply date filters
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__gte=start_dt)
            except ValueError:
                return Response({
                    'success': False,
                    'message': 'Invalid start_date format. Use YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__lte=end_dt)
            except ValueError:
                return Response({
                    'success': False,
                    'message': 'Invalid end_date format. Use YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate statistics
        stats = queryset.aggregate(
            total_purchases=Count('id'),
            total_amount=Sum('amount'),
            total_credits=Sum('credits'),
            average_purchase_amount=Avg('amount'),
            last_purchase_date=Max('created_at')
        )
        
        # Count by status
        status_counts = queryset.values('status').annotate(count=Count('id'))
        status_dict = {item['status']: item['count'] for item in status_counts}
        
        summary_data = {
            'total_purchases': stats['total_purchases'] or 0,
            'total_amount': float(stats['total_amount'] or 0),
            'total_credits': stats['total_credits'] or 0,
            'completed_purchases': status_dict.get('completed', 0),
            'pending_purchases': status_dict.get('pending', 0),
            'failed_purchases': status_dict.get('failed', 0),
            'cancelled_purchases': status_dict.get('cancelled', 0),
            'refunded_purchases': status_dict.get('refunded', 0),
            'average_purchase_amount': float(stats['average_purchase_amount'] or 0),
            'last_purchase_date': stats['last_purchase_date'].isoformat() if stats['last_purchase_date'] else None
        }
        
        return Response({
            'success': True,
            'data': summary_data
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': 'Failed to retrieve purchase history summary',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def purchase_detail(request, purchase_id):
    """
    Get detailed information about a specific purchase.
    GET /api/messaging/purchase-history/{purchase_id}/
    """
    try:
        from billing.models import Purchase
        from django.shortcuts import get_object_or_404
        
        # Get purchase (filter by user for security)
        purchase = get_object_or_404(Purchase, id=purchase_id, user=request.user)
        
        # Serialize purchase data
        purchase_data = {
            'id': str(purchase.id),
            'invoice_number': purchase.invoice_number,
            'package': {
                'id': str(purchase.package.id),
                'name': purchase.package.name,
                'package_type': purchase.package.package_type,
                'credits': purchase.package.credits,
                'price': float(purchase.package.price),
                'unit_price': float(purchase.package.unit_price),
                'features': purchase.package.features,
                'is_popular': purchase.package.is_popular
            },
            'credits': purchase.credits,
            'amount': float(purchase.amount),
            'unit_price': float(purchase.unit_price),
            'payment_method': purchase.payment_method,
            'payment_method_display': purchase.get_payment_method_display(),
            'payment_reference': purchase.payment_reference,
            'status': purchase.status,
            'status_display': purchase.get_status_display(),
            'created_at': purchase.created_at.isoformat(),
            'completed_at': purchase.completed_at.isoformat() if purchase.completed_at else None,
            'updated_at': purchase.updated_at.isoformat()
        }
        
        return Response({
            'success': True,
            'data': purchase_data
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': 'Failed to retrieve purchase details',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
