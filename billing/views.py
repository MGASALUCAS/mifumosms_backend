"""
Views for billing functionality (no implicit 'free' plan; no auto-creation).
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import BillingPlan, Subscription, UsageRecord
from .serializers import (
    BillingPlanSerializer, SubscriptionSerializer, UsageRecordSerializer,
)


# ==============================
# Plans
# ==============================

class PlanListView(generics.ListAPIView):
    """List available subscription plans."""
    serializer_class = BillingPlanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # No user/tenant dependency -> safe for schema generation
        return BillingPlan.objects.filter(is_active=True).order_by('price')


# ==============================
# Subscription
# ==============================

class SubscriptionDetailView(generics.RetrieveAPIView):
    """Get current subscription details (no auto-create, no implicit free plan)."""
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # When generating schema, drf_yasg sets this flag and request.user is Anonymous
        if getattr(self, "swagger_fake_view", False):
            # Return a harmless in-memory instance without DB writes
            return Subscription(
                status='inactive',
                current_period_start=timezone.now(),
                current_period_end=timezone.now() + timezone.timedelta(days=30),
            )

        tenant = getattr(self.request.user, "tenant", None)
        if not tenant:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("User is not associated with any tenant")

        subscription = (
            Subscription.objects
            .select_related("plan")
            .filter(tenant=tenant)
            .first()
        )
        if not subscription:
            from rest_framework.exceptions import NotFound
            raise NotFound("No subscription found. Please select a plan and create a subscription.")

        if subscription.plan_id is None:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Subscription exists but has no plan assigned. Please assign a plan.")

        return subscription


# ==============================
# Usage
# ==============================

class UsageRecordListView(generics.ListAPIView):
    """List usage records for tenant."""
    serializer_class = UsageRecordSerializer
    permission_classes = [IsAuthenticated]

    # Prevent global filter backends from running during schema gen
    filter_backends = []
    ordering = ['-created_at']

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return UsageRecord.objects.none()

        tenant = getattr(self.request.user, "tenant", None)
        if not tenant:
            return UsageRecord.objects.none()

        return UsageRecord.objects.filter(tenant=tenant).order_by('-created_at')


# ==============================
# Overview
# ==============================

@swagger_auto_schema(
    method='get',
    operation_description="Get billing overview for the authenticated user's tenant (no implicit free plan).",
    responses={
        200: openapi.Response(
            description="Success",
            examples={
                "application/json": {
                    "success": True,
                    "data": {
                        "subscription": {
                            "plan_id": "uuid",
                            "plan_name": "Pro",
                            "status": "active",
                            "current_period_end": "2025-10-31T23:59:59Z",
                            "is_active": True,
                        },
                        "usage": {
                            "total_credits": 12345,
                            "total_cost": 456.78,
                        },
                    }
                }
            },
        ),
        404: "No subscription found",
        400: "User not in a tenant / subscription without plan",
        500: "Internal Server Error",
    },
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def billing_overview(request):
    """
    Get billing overview for tenant.
    GET /api/billing/overview/
    """
    try:
        tenant = getattr(request.user, "tenant", None)
        if not tenant:
            return Response(
                {
                    'success': False,
                    'message': 'User is not associated with any tenant. Please contact support.',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription = (
            Subscription.objects
            .select_related("plan")
            .filter(tenant=tenant)
            .first()
        )
        if not subscription:
            # Don’t auto-create; surface a clear, helpful 404 with available plans
            plans = list(
                BillingPlan.objects
                .filter(is_active=True)
                .values('id', 'name', 'plan_type', 'price')
                .order_by('price')
            )
            return Response(
                {
                    'success': False,
                    'message': 'No subscription found. Please select a plan and create a subscription.',
                    'error_code': 'NO_SUBSCRIPTION',
                    'available_plans': plans,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if subscription.plan_id is None:
            return Response(
                {
                    'success': False,
                    'message': 'Subscription exists but has no plan assigned. Please assign a plan.',
                    'error_code': 'SUBSCRIPTION_MISSING_PLAN',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        usage_stats = UsageRecord.objects.filter(tenant=tenant).aggregate(
            total_credits=Sum('credits_used'),
            total_cost=Sum('cost'),
        )

        return Response(
            {
                'success': True,
                'data': {
                    'subscription': {
                        'plan_id': str(subscription.plan.id),
                        'plan_name': subscription.plan.name,
                        'status': subscription.status,
                        'current_period_end': subscription.current_period_end.isoformat()
                        if subscription.current_period_end else None,
                        'is_active': subscription.is_active,
                    },
                    'usage': {
                        'total_credits': usage_stats['total_credits'] or 0,
                        'total_cost': float(usage_stats['total_cost'] or 0),
                    },
                },
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {
                'success': False,
                'message': 'Failed to retrieve billing overview',
                'error': str(e),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
