"""
Views for billing functionality.
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Sum, Q

from .models import BillingPlan, Subscription, UsageRecord
from .serializers import (
    BillingPlanSerializer, SubscriptionSerializer, UsageRecordSerializer
)
from core.permissions import IsTenantMember, IsTenantAdmin


class PlanListView(generics.ListAPIView):
    """List available subscription plans."""
    serializer_class = BillingPlanSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return BillingPlan.objects.filter(is_active=True).order_by('price')


class SubscriptionDetailView(generics.RetrieveAPIView):
    """Get current subscription details."""
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        tenant = self.request.user.tenant
        if not tenant:
            raise ValueError("User is not associated with any tenant")
        
        subscription, created = Subscription.objects.get_or_create(
            tenant=tenant,
            defaults={
                'plan': BillingPlan.objects.filter(plan_type='free').first(),
                'status': 'active',
                'current_period_start': timezone.now(),
                'current_period_end': timezone.now() + timezone.timedelta(days=30)
            }
        )
        return subscription


class UsageRecordListView(generics.ListAPIView):
    """List usage records for tenant."""
    serializer_class = UsageRecordSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        tenant = self.request.user.tenant
        if not tenant:
            return UsageRecord.objects.none()
        
        return UsageRecord.objects.filter(tenant=tenant).order_by('-created_at')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def billing_overview(request):
    """
    Get billing overview for tenant.
    GET /api/billing/overview/
    """
    try:
        tenant = request.user.tenant
        if not tenant:
            return Response({
                'success': False,
                'message': 'User is not associated with any tenant. Please contact support.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get subscription
        subscription, created = Subscription.objects.get_or_create(
            tenant=tenant,
            defaults={
                'plan': BillingPlan.objects.filter(plan_type='free').first(),
                'status': 'active',
                'current_period_start': timezone.now(),
                'current_period_end': timezone.now() + timezone.timedelta(days=30)
            }
        )
        
        # Get usage statistics
        usage_stats = UsageRecord.objects.filter(tenant=tenant).aggregate(
            total_credits=Sum('credits_used'),
            total_cost=Sum('cost')
        )
        
        return Response({
            'success': True,
            'data': {
                'subscription': {
                    'plan_name': subscription.plan.name,
                    'status': subscription.status,
                    'current_period_end': subscription.current_period_end.isoformat(),
                    'is_active': subscription.is_active
                },
                'usage': {
                    'total_credits': usage_stats['total_credits'] or 0,
                    'total_cost': float(usage_stats['total_cost'] or 0)
                }
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': 'Failed to retrieve billing overview',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)