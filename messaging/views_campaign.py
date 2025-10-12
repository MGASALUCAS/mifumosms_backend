"""
Campaign API views for Mifumo WMS.
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.permissions import IsOwnerOrReadOnly, CanEditCampaign, CanStartCampaign, CanPauseCampaign, CanCancelCampaign
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Sum
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from .models import Campaign
from .models import Contact, Segment, Template
from .serializers import CampaignSerializer, CampaignCreateSerializer, CampaignUpdateSerializer

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
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return CampaignUpdateSerializer
        return CampaignSerializer

    def get_queryset(self):
        return Campaign.objects.filter(
            created_by=self.request.user
        ).select_related('template').prefetch_related('target_contacts', 'target_segments')


@api_view(['POST'])
@permission_classes([IsAuthenticated, CanStartCampaign])
def start_campaign(request, campaign_id):
    """
    Start a campaign.
    POST /api/messaging/campaigns/{id}/start/
    """
    try:
        campaign = get_object_or_404(
            Campaign,
            id=campaign_id,
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
            'campaign': CampaignSerializer(campaign).data
        })

    except Exception as e:
        logger.error(f"Error starting campaign {campaign_id}: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to start campaign'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated, CanPauseCampaign])
def pause_campaign(request, campaign_id):
    """
    Pause a campaign.
    POST /api/messaging/campaigns/{id}/pause/
    """
    try:
        campaign = get_object_or_404(
            Campaign,
            id=campaign_id,
            created_by=request.user
        )

        if not campaign.can_pause:
            return Response({
                'success': False,
                'message': f'Cannot pause campaign in {campaign.status} status'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Pause the campaign
        campaign.pause_campaign()

        return Response({
            'success': True,
            'message': 'Campaign paused successfully',
            'campaign': CampaignSerializer(campaign).data
        })

    except Exception as e:
        logger.error(f"Error pausing campaign {campaign_id}: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to pause campaign'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated, CanCancelCampaign])
def cancel_campaign(request, campaign_id):
    """
    Cancel a campaign.
    POST /api/messaging/campaigns/{id}/cancel/
    """
    try:
        campaign = get_object_or_404(
            Campaign,
            id=campaign_id,
            created_by=request.user
        )

        if not campaign.can_cancel:
            return Response({
                'success': False,
                'message': f'Cannot cancel campaign in {campaign.status} status'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Cancel the campaign
        campaign.cancel_campaign()

        return Response({
            'success': True,
            'message': 'Campaign cancelled successfully',
            'campaign': CampaignSerializer(campaign).data
        })

    except Exception as e:
        logger.error(f"Error cancelling campaign {campaign_id}: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to cancel campaign'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def campaign_permissions(request, campaign_id):
    """
    Get campaign permissions for the current user.
    GET /api/messaging/campaigns/{id}/permissions/
    """
    try:
        campaign = get_object_or_404(
            Campaign,
            id=campaign_id,
            created_by=request.user
        )

        permissions = {
            'can_view': True,  # User can always view their own campaigns
            'can_edit': campaign.status == 'draft',
            'can_delete': campaign.status == 'draft',
            'can_start': campaign.can_start,
            'can_pause': campaign.can_pause,
            'can_cancel': campaign.can_cancel,
            'can_duplicate': True,  # User can always duplicate their campaigns
            'can_view_analytics': True,  # User can always view analytics of their campaigns
        }

        return Response({
            'success': True,
            'data': {
                'campaign_id': str(campaign.id),
                'campaign_name': campaign.name,
                'campaign_status': campaign.status,
                'permissions': permissions,
                'status_info': {
                    'is_draft': campaign.status == 'draft',
                    'is_running': campaign.status == 'running',
                    'is_paused': campaign.status == 'paused',
                    'is_completed': campaign.status == 'completed',
                    'is_cancelled': campaign.status == 'cancelled',
                }
            }
        })

    except Exception as e:
        logger.error(f"Campaign permissions error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to get campaign permissions'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def campaign_analytics(request, campaign_id):
    """
    Get analytics for a specific campaign.
    GET /api/messaging/campaigns/{id}/analytics/
    """
    try:
        campaign = get_object_or_404(
            Campaign,
            id=campaign_id,
            created_by=request.user
        )

        # Calculate analytics
        analytics = {
            'campaign_id': str(campaign.id),
            'campaign_name': campaign.name,
            'status': campaign.status,
            'total_recipients': campaign.total_recipients,
            'sent_count': campaign.sent_count,
            'delivered_count': campaign.delivered_count,
            'read_count': campaign.read_count,
            'failed_count': campaign.failed_count,
            'progress_percentage': campaign.progress_percentage,
            'delivery_rate': campaign.delivery_rate,
            'read_rate': campaign.read_rate,
            'estimated_cost': float(campaign.estimated_cost),
            'actual_cost': float(campaign.actual_cost),
            'created_at': campaign.created_at,
            'started_at': campaign.started_at,
            'completed_at': campaign.completed_at,
        }

        return Response({
            'success': True,
            'analytics': analytics
        })

    except Exception as e:
        logger.error(f"Error getting campaign analytics {campaign_id}: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to get campaign analytics'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def duplicate_campaign(request, campaign_id):
    """
    Duplicate a campaign.
    POST /api/messaging/campaigns/{id}/duplicate/
    """
    try:
        original_campaign = get_object_or_404(
            Campaign,
            id=campaign_id,
            created_by=request.user
        )

        # Create duplicate
        duplicate = Campaign.objects.create(
            name=f"{original_campaign.name} (Copy)",
            description=original_campaign.description,
            campaign_type=original_campaign.campaign_type,
            message_text=original_campaign.message_text,
            template=original_campaign.template,
            target_criteria=original_campaign.target_criteria,
            settings=original_campaign.settings,
            is_recurring=original_campaign.is_recurring,
            recurring_schedule=original_campaign.recurring_schedule,
            created_by=request.user
        )

        # Copy targeting
        duplicate.target_contacts.set(original_campaign.target_contacts.all())
        duplicate.target_segments.set(original_campaign.target_segments.all())

        # Update statistics
        duplicate.update_statistics()

        return Response({
            'success': True,
            'message': 'Campaign duplicated successfully',
            'campaign': CampaignSerializer(duplicate).data
        })

    except Exception as e:
        logger.error(f"Error duplicating campaign {campaign_id}: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to duplicate campaign'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_campaigns_summary(request):
    """
    Get summary of user's campaigns.
    GET /api/messaging/campaigns/summary/
    """
    try:
        user = request.user

        # Get campaign counts by status
        status_counts = Campaign.objects.filter(created_by=user).values('status').annotate(
            count=Count('id')
        )

        # Get total statistics
        total_stats = Campaign.objects.filter(created_by=user).aggregate(
            total_campaigns=Count('id'),
            total_recipients=Sum('total_recipients'),
            total_sent=Sum('sent_count'),
            total_delivered=Sum('delivered_count'),
            total_read=Sum('read_count'),
            total_failed=Sum('failed_count'),
            total_estimated_cost=Sum('estimated_cost'),
            total_actual_cost=Sum('actual_cost')
        )

        # Get recent campaigns
        recent_campaigns = Campaign.objects.filter(created_by=user).order_by('-created_at')[:5]

        summary = {
            'status_counts': {item['status']: item['count'] for item in status_counts},
            'total_stats': total_stats,
            'recent_campaigns': CampaignSerializer(recent_campaigns, many=True).data
        }

        return Response({
            'success': True,
            'summary': summary
        })

    except Exception as e:
        logger.error(f"Error getting campaign summary: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to get campaign summary'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
