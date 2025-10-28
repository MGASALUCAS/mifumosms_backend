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

from .models import BillingPlan, Subscription, UsageRecord, SMSBalance
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
            # Don't auto-create; surface a clear, helpful 404 with available plans
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

        # Get SMS balance
        sms_balance, _ = SMSBalance.objects.get_or_create(tenant=tenant)

        # Get recent purchases
        from .models import Purchase, PaymentTransaction
        recent_purchases = Purchase.objects.filter(
            tenant=tenant
        ).order_by('-created_at')[:5].values(
            'id', 'invoice_number', 'amount', 'credits', 'status', 'created_at'
        )
        
        # Get active payments
        active_payments = PaymentTransaction.objects.filter(
            tenant=tenant,
            status__in=['pending', 'processing']
        ).order_by('-created_at')[:5].values(
            'id', 'order_id', 'amount', 'status', 'created_at'
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
                    'sms_balance': {
                        'credits': sms_balance.credits,
                        'total_purchased': sms_balance.total_purchased,
                        'total_used': sms_balance.total_used,
                    },
                    'usage': {
                        'total_credits': usage_stats['total_credits'] or 0,
                        'total_cost': float(usage_stats['total_cost'] or 0),
                    },
                    'usage_summary': {
                        'total_credits': usage_stats['total_credits'] or 0,
                        'total_cost': float(usage_stats['total_cost'] or 0),
                        'current_balance': sms_balance.credits,
                    },
                    'recent_purchases': list(recent_purchases),
                    'active_payments': list(active_payments),
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


@swagger_auto_schema(
    method='get',
    operation_description="Get billing information for settings page including plan, usage, and payment details.",
    responses={
        200: openapi.Response(
            description="Success",
            examples={
                "application/json": {
                    "success": True,
                    "data": {
                        "current_plan": {
                            "name": "Professional",
                            "price": 99.00,
                            "currency": "TZS",
                            "billing_cycle": "monthly",
                            "max_messages": 10000,
                            "status": "active",
                            "features": ["API Access", "Priority Support"]
                        },
                        "usage_this_month": {
                            "messages_sent": 7245,
                            "limit": 10000,
                            "percentage_used": 72.45,
                            "next_billing_date": "2024-04-01",
                            "next_billing_amount": 99.00
                        },
                        "payment_method": {
                            "type": "card",
                            "last_four": "4242",
                            "expiry_month": 12,
                            "expiry_year": 2025,
                            "card_brand": "VISA"
                        }
                    }
                }
            },
        ),
        404: "No subscription found",
        400: "User not in a tenant",
        500: "Internal Server Error",
    },
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def billing_info(request):
    """
    Get billing information for settings page.
    Returns current plan details, usage this month, and payment method.
    GET /api/billing/info/
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

        # Get or create SMS balance
        sms_balance, _ = SMSBalance.objects.get_or_create(tenant=tenant)

        # Get current subscription
        subscription = Subscription.objects.select_related("plan").filter(tenant=tenant).first()
        
        current_plan_data = None
        usage_data = None
        payment_method_data = None

        # Current Plan Information
        if subscription and subscription.plan:
            plan = subscription.plan
            current_plan_data = {
                'id': str(plan.id),
                'name': plan.name,
                'price': float(plan.price),
                'currency': plan.currency,
                'billing_cycle': plan.billing_cycle,
                'plan_type': plan.plan_type,
                'max_messages': plan.max_sms_per_month,
                'status': subscription.status,
                'is_active': subscription.is_active,
                'features': plan.features or [],
                'current_period_start': subscription.current_period_start.isoformat() if subscription.current_period_start else None,
                'current_period_end': subscription.current_period_end.isoformat() if subscription.current_period_end else None,
            }
        else:
            # No subscription - show prepaid credit information
            current_plan_data = {
                'name': 'Prepaid',
                'price': 0.00,
                'currency': 'TZS',
                'billing_cycle': 'prepaid',
                'plan_type': 'prepaid',
                'max_messages': None,
                'status': 'active',
                'is_active': True,
                'features': ['Pay as you go', 'No monthly commitment'],
            }

        # Usage This Month
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Get usage records for current month
        monthly_usage = UsageRecord.objects.filter(
            tenant=tenant,
            created_at__gte=month_start
        ).aggregate(
            total_credits=Sum('credits_used'),
            total_cost=Sum('cost')
        )

        messages_sent = monthly_usage['total_credits'] or 0
        limit = current_plan_data.get('max_messages') if current_plan_data else None
        percentage_used = (messages_sent / limit * 100) if limit and limit > 0 else 0
        
        usage_data = {
            'messages_sent': messages_sent,
            'limit': limit,
            'percentage_used': round(percentage_used, 2),
            'cost': float(monthly_usage['total_cost'] or 0),
        }

        # Calculate next billing date
        if subscription and subscription.current_period_end:
            usage_data['next_billing_date'] = subscription.current_period_end.isoformat()
            if subscription.plan:
                usage_data['next_billing_amount'] = float(subscription.plan.price)
        else:
            usage_data['next_billing_date'] = None
            usage_data['next_billing_amount'] = 0.00

        # Payment Method Information
        # Get the most recent completed payment transaction
        from .models import PaymentTransaction
        recent_payment = PaymentTransaction.objects.filter(
            tenant=tenant,
            status='completed'
        ).order_by('-completed_at').first()

        if recent_payment:
            payment_method_data = {
                'type': recent_payment.payment_method,
                'payment_method_display': recent_payment.get_payment_method_display(),
                'last_transaction_date': recent_payment.completed_at.isoformat() if recent_payment.completed_at else None,
                'last_transaction_amount': float(recent_payment.amount) if recent_payment.amount else 0.00,
            }
        else:
            payment_method_data = {
                'type': None,
                'payment_method_display': 'No payment method on file',
                'last_transaction_date': None,
                'last_transaction_amount': 0.00,
            }

        # SMS Balance Information (for prepaid customers)
        sms_balance_data = {
            'credits': sms_balance.credits,
            'total_purchased': sms_balance.total_purchased,
            'total_used': sms_balance.total_used,
            'last_updated': sms_balance.last_updated.isoformat() if sms_balance.last_updated else None,
        }

        return Response(
            {
                'success': True,
                'data': {
                    'current_plan': current_plan_data,
                    'usage_this_month': usage_data,
                    'payment_method': payment_method_data,
                    'sms_balance': sms_balance_data,
                },
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {
                'success': False,
                'message': 'Failed to retrieve billing information',
                'error': str(e),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
