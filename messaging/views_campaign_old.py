"""
Smart Campaign views for Mifumo WMS.
Extremely simple and efficient campaign management.
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Count, Sum, Q, F
from django.db import transaction
from datetime import datetime, timedelta
import logging

from .models import Campaign
from .models import Contact, Segment, Template
from .serializers import CampaignSerializer, CampaignCreateSerializer, CampaignUpdateSerializer
# Removed tenant import - no longer needed

logger = logging.getLogger(__name__)


class CampaignListView(generics.ListCreateAPIView):
    """
    List and create campaigns for the authenticated user.
    GET /api/messaging/campaigns/
    POST /api/messaging/campaigns/
    """
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CampaignCreateSerializer
        return CampaignSerializer
    
    def get_queryset(self):
        # Filter by user's campaigns only
        queryset = Campaign.objects.filter(
            created_by=self.request.user
        ).select_related('template').prefetch_related('target_contacts', 'target_segments')
        
        # Add filtering
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        campaign_type = self.request.query_params.get('type')
        if campaign_type:
            queryset = queryset.filter(campaign_type=campaign_type)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Create campaign for the authenticated user."""
        campaign = serializer.save(
            created_by=self.request.user
        )
        
        # Calculate recipients and update statistics
        campaign.update_statistics()
        
        return campaign


class CampaignDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, update, or delete a specific campaign.
    GET /api/messaging/campaigns/{id}/
    PUT /api/messaging/campaigns/{id}/
    DELETE /api/messaging/campaigns/{id}/
    """
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return CampaignUpdateSerializer
        return CampaignSerializer
    
    def get_queryset(self):
        return Campaign.objects.filter(
            created_by=self.request.user
        ).select_related('template').prefetch_related('target_contacts', 'target_segments')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_campaign(request, campaign_id):
    """
    Start a campaign.
    POST /api/messaging/campaigns/{id}/start/
    """
    try:
        tenant = request.user.tenant
        if not tenant:
            return Response({
                'success': False,
                'message': 'User is not associated with any tenant. Please contact support.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        campaign = get_object_or_404(
            Campaign,
            id=campaign_id,
            tenant=tenant,
            created_by=request.user
        )
        
        if not campaign.can_start:
            return Response({
                'success': False,
                'message': f'Cannot start campaign in {campaign.status} status'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Start the campaign
        campaign.start_campaign()
        
        return Response({
            'success': True,
            'message': 'Campaign started successfully',
            'data': {
                'campaign_id': str(campaign.id),
                'status': campaign.status,
                'started_at': campaign.started_at.isoformat() if campaign.started_at else None
            }
        })
        
    except Exception as e:
        logger.error(f"Start campaign error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to start campaign',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pause_campaign(request, campaign_id):
    """
    Pause a campaign.
    POST /api/messaging/campaigns/{id}/pause/
    """
    try:
        tenant = request.user.tenant
        if not tenant:
            return Response({
                'success': False,
                'message': 'User is not associated with any tenant. Please contact support.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        campaign = get_object_or_404(
            Campaign,
            id=campaign_id,
            tenant=tenant,
            created_by=request.user
        )
        
        if not campaign.can_pause:
            return Response({
                'success': False,
                'message': f'Cannot pause campaign in {campaign.status} status'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        campaign.pause_campaign()
        
        return Response({
            'success': True,
            'message': 'Campaign paused successfully',
            'data': {
                'campaign_id': str(campaign.id),
                'status': campaign.status
            }
        })
        
    except Exception as e:
        logger.error(f"Pause campaign error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to pause campaign',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_campaign(request, campaign_id):
    """
    Cancel a campaign.
    POST /api/messaging/campaigns/{id}/cancel/
    """
    try:
        tenant = request.user.tenant
        if not tenant:
            return Response({
                'success': False,
                'message': 'User is not associated with any tenant. Please contact support.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        campaign = get_object_or_404(
            Campaign,
            id=campaign_id,
            tenant=tenant,
            created_by=request.user
        )
        
        if not campaign.can_cancel:
            return Response({
                'success': False,
                'message': f'Cannot cancel campaign in {campaign.status} status'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        campaign.cancel_campaign()
        
        return Response({
            'success': True,
            'message': 'Campaign cancelled successfully',
            'data': {
                'campaign_id': str(campaign.id),
                'status': campaign.status
            }
        })
        
    except Exception as e:
        logger.error(f"Cancel campaign error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to cancel campaign',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def campaign_analytics(request, campaign_id):
    """
    Get detailed analytics for a campaign.
    GET /api/messaging/campaigns/{id}/analytics/
    """
    try:
        tenant = request.user.tenant
        if not tenant:
            return Response({
                'success': False,
                'message': 'User is not associated with any tenant. Please contact support.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        campaign = get_object_or_404(
            Campaign,
            id=campaign_id,
            tenant=tenant,
            created_by=request.user
        )
        
        # Get analytics data
        analytics_data = {
            'campaign_id': str(campaign.id),
            'campaign_name': campaign.name,
            'status': campaign.status,
            'overview': {
                'total_recipients': campaign.total_recipients,
                'sent_count': campaign.sent_count,
                'delivered_count': campaign.delivered_count,
                'read_count': campaign.read_count,
                'failed_count': campaign.failed_count,
                'progress_percentage': campaign.progress_percentage,
                'delivery_rate': campaign.delivery_rate,
                'read_rate': campaign.read_rate,
            },
            'costs': {
                'estimated_cost': float(campaign.estimated_cost),
                'actual_cost': float(campaign.actual_cost),
            },
            'timing': {
                'created_at': campaign.created_at.isoformat(),
                'scheduled_at': campaign.scheduled_at.isoformat() if campaign.scheduled_at else None,
                'started_at': campaign.started_at.isoformat() if campaign.started_at else None,
                'completed_at': campaign.completed_at.isoformat() if campaign.completed_at else None,
            }
        }
        
        # Get daily analytics if campaign is running or completed
        if campaign.status in ['running', 'completed']:
            daily_analytics = CampaignAnalytics.objects.filter(
                campaign=campaign
            ).order_by('-date')[:30]  # Last 30 days
            
            analytics_data['daily_breakdown'] = [
                {
                    'date': analytics.date.isoformat(),
                    'sent': analytics.sent_count,
                    'delivered': analytics.delivered_count,
                    'read': analytics.read_count,
                    'failed': analytics.failed_count,
                    'cost': float(analytics.cost)
                }
                for analytics in daily_analytics
            ]
        
        return Response({
            'success': True,
            'data': analytics_data
        })
        
    except Exception as e:
        logger.error(f"Campaign analytics error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to retrieve campaign analytics',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_campaigns_summary(request):
    """
    Get summary of user's campaigns.
    GET /api/messaging/campaigns/summary/
    """
    try:
        tenant = request.user.tenant
        if not tenant:
            return Response({
                'success': False,
                'message': 'User is not associated with any tenant. Please contact support.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get user's campaigns
        campaigns = Campaign.objects.filter(
            tenant=tenant,
            created_by=request.user
        )
        
        # Calculate summary statistics
        total_campaigns = campaigns.count()
        active_campaigns = campaigns.filter(status__in=['running', 'scheduled']).count()
        completed_campaigns = campaigns.filter(status='completed').count()
        
        # Calculate totals
        totals = campaigns.aggregate(
            total_recipients=Sum('total_recipients'),
            total_sent=Sum('sent_count'),
            total_delivered=Sum('delivered_count'),
            total_read=Sum('read_count'),
            total_cost=Sum('actual_cost')
        )
        
        # Recent campaigns (last 5)
        recent_campaigns = campaigns.order_by('-created_at')[:5]
        recent_data = []
        
        for campaign in recent_campaigns:
            recent_data.append({
                'id': str(campaign.id),
                'name': campaign.name,
                'type': campaign.campaign_type,
                'status': campaign.status,
                'progress': campaign.progress_percentage,
                'recipients': campaign.total_recipients,
                'sent': campaign.sent_count,
                'delivered': campaign.delivered_count,
                'created_at': campaign.created_at.isoformat(),
                'created_at_human': _get_human_time(campaign.created_at)
            })
        
        return Response({
            'success': True,
            'data': {
                'summary': {
                    'total_campaigns': total_campaigns,
                    'active_campaigns': active_campaigns,
                    'completed_campaigns': completed_campaigns,
                    'total_recipients': totals['total_recipients'] or 0,
                    'total_sent': totals['total_sent'] or 0,
                    'total_delivered': totals['total_delivered'] or 0,
                    'total_read': totals['total_read'] or 0,
                    'total_cost': float(totals['total_cost'] or 0)
                },
                'recent_campaigns': recent_data
            }
        })
        
    except Exception as e:
        logger.error(f"Campaign summary error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to retrieve campaign summary',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def duplicate_campaign(request, campaign_id):
    """
    Duplicate a campaign.
    POST /api/messaging/campaigns/{id}/duplicate/
    """
    try:
        tenant = request.user.tenant
        if not tenant:
            return Response({
                'success': False,
                'message': 'User is not associated with any tenant. Please contact support.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        original_campaign = get_object_or_404(
            Campaign,
            id=campaign_id,
            tenant=tenant,
            created_by=request.user
        )
        
        # Create duplicate
        with transaction.atomic():
            duplicate_campaign = Campaign.objects.create(
                tenant=tenant,
                created_by=request.user,
                name=f"{original_campaign.name} (Copy)",
                description=original_campaign.description,
                campaign_type=original_campaign.campaign_type,
                message_text=original_campaign.message_text,
                template=original_campaign.template,
                target_criteria=original_campaign.target_criteria,
                settings=original_campaign.settings,
                is_recurring=original_campaign.is_recurring,
                recurring_schedule=original_campaign.recurring_schedule,
                status='draft'  # Always start as draft
            )
            
            # Copy targeting
            if original_campaign.target_segments.exists():
                duplicate_campaign.target_segments.set(original_campaign.target_segments.all())
            
            if original_campaign.target_contacts.exists():
                duplicate_campaign.target_contacts.set(original_campaign.target_contacts.all())
            
            # Update statistics
            duplicate_campaign.update_statistics()
        
        return Response({
            'success': True,
            'message': 'Campaign duplicated successfully',
            'data': {
                'original_id': str(original_campaign.id),
                'duplicate_id': str(duplicate_campaign.id),
                'duplicate_name': duplicate_campaign.name
            }
        })
        
    except Exception as e:
        logger.error(f"Duplicate campaign error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to duplicate campaign',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _get_human_time(dt):
    """Convert datetime to human readable format."""
    now = timezone.now()
    diff = now - dt
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"
