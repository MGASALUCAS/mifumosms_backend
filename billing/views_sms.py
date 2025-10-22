"""
SMS billing and purchase views for Mifumo WMS.
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from django.db.models import Sum  # <-- needed for aggregates
from datetime import datetime, timedelta
import logging
import uuid

from .models import (
    SMSPackage,
    SMSBalance,
    Purchase,
    UsageRecord,
    BillingPlan,
    Subscription,
)
from .serializers import (
    SMSPackageSerializer,
    PurchaseSerializer,
    PurchaseCreateSerializer,
    SMSBalanceSerializer,
    UsageRecordSerializer,
    BillingPlanSerializer,
    SubscriptionSerializer,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers so schema generation (drf_yasg) / anonymous requests don't crash
# ---------------------------------------------------------------------------
def _is_schema_or_anon(view) -> bool:
    """True if drf_yasg is generating schema or if the request is anonymous."""
    if getattr(view, "swagger_fake_view", False):
        return True
    user = getattr(view, "request", None)
    if user is None:
        return True
    user = getattr(view.request, "user", None)
    return not getattr(user, "is_authenticated", False)


class SMSPackageListView(generics.ListAPIView):
    """
    List available SMS packages.
    GET /api/billing/sms/packages/
    """
    serializer_class = SMSPackageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Safe for schema gen too – no user access here
        # Exclude custom packages from the regular package list
        return SMSPackage.objects.filter(
            is_active=True,
            package_type__in=['lite', 'standard', 'pro', 'enterprise']
        ).order_by("price")


class SMSBalanceView(generics.RetrieveAPIView):
    """
    Get SMS balance for tenant.
    GET /api/billing/sms/balance/
    """
    serializer_class = SMSBalanceSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        tenant = getattr(self.request.user, "tenant", None)
        if not tenant:
            # keep this a clean app error rather than AttributeError
            raise ValueError("User is not associated with any tenant")
        balance, _ = SMSBalance.objects.get_or_create(tenant=tenant)
        return balance

    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except ValueError as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_purchase(request):
    """
    Create a new SMS credit purchase.
    POST /api/billing/sms/purchase/

    Request Body:
    {
        "package_id": "uuid",
        "payment_method": "mpesa",
        "payment_reference": "optional"
    }
    """
    try:
        tenant = getattr(request.user, "tenant", None)
        if not tenant:
            return Response(
                {
                    "success": False,
                    "message": "User is not associated with any tenant. Please contact support.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = PurchaseCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Validation error",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = serializer.validated_data
        package = get_object_or_404(SMSPackage, id=data["package_id"], is_active=True)

        # Generate invoice number
        invoice_number = f"INV-{timezone.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

        # Create purchase record
        purchase = Purchase.objects.create(
            tenant=tenant,
            user=request.user,
            package=package,
            invoice_number=invoice_number,
            amount=package.price,
            credits=package.credits,
            unit_price=package.unit_price,
            payment_method=data["payment_method"],
            payment_reference=data.get("payment_reference", ""),
            status="pending",
        )

        # For demo purposes, auto-complete the purchase.
        # In production, integrate with your payment gateway/webhooks.
        purchase.complete_purchase()

        return Response(
            {
                "success": True,
                "message": "Purchase created successfully",
                "data": {
                    "purchase_id": str(purchase.id),
                    "invoice_number": purchase.invoice_number,
                    "credits": purchase.credits,
                    "amount": float(purchase.amount),
                    "status": purchase.status,
                    "new_balance": tenant.sms_balance.credits,
                },
            },
            status=status.HTTP_201_CREATED,
        )

    except Exception as e:
        logger.error(f"Purchase creation error: {str(e)}")
        return Response(
            {
                "success": False,
                "message": "Failed to create purchase",
                "error": str(e),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class PurchaseListView(generics.ListAPIView):
    """
    List purchase history for tenant.
    GET /api/billing/sms/purchases/
    """
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Avoid AnonymousUser.tenant error during schema gen
        if _is_schema_or_anon(self):
            return Purchase.objects.none()

        tenant = getattr(self.request.user, "tenant", None)
        if not tenant:
            return Purchase.objects.none()

        return Purchase.objects.filter(tenant=tenant).order_by("-created_at")


class PurchaseDetailView(generics.RetrieveAPIView):
    """
    Get purchase details.
    GET /api/billing/sms/purchases/{id}/
    """
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Avoid AnonymousUser.tenant error during schema gen
        if _is_schema_or_anon(self):
            return Purchase.objects.none()

        tenant = getattr(self.request.user, "tenant", None)
        if not tenant:
            return Purchase.objects.none()

        return Purchase.objects.filter(tenant=tenant)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def complete_purchase(request, purchase_id):
    """
    Complete a pending purchase (for payment gateway integration).
    POST /api/billing/sms/purchases/{id}/complete/
    """
    try:
        tenant = getattr(request.user, "tenant", None)
        if not tenant:
            return Response(
                {
                    "success": False,
                    "message": "User is not associated with any tenant. Please contact support.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        purchase = get_object_or_404(Purchase, id=purchase_id, tenant=tenant)

        if purchase.status != "pending":
            return Response(
                {"success": False, "message": f"Purchase is already {purchase.status}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Complete the purchase
        if purchase.complete_purchase():
            return Response(
                {
                    "success": True,
                    "message": "Purchase completed successfully",
                    "data": {
                        "purchase_id": str(purchase.id),
                        "credits": purchase.credits,
                        "new_balance": tenant.sms_balance.credits,
                    },
                }
            )
        else:
            return Response(
                {"success": False, "message": "Failed to complete purchase"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    except Exception as e:
        logger.error(f"Purchase completion error: {str(e)}")
        return Response(
            {
                "success": False,
                "message": "Failed to complete purchase",
                "error": str(e),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def purchase_history(request):
    """
    Get detailed purchase history with filtering.
    GET /api/billing/sms/purchases/history/

    Query Parameters:
    - status: Filter by purchase status
    - start_date: Filter from date (YYYY-MM-DD)
    - end_date: Filter to date (YYYY-MM-DD)
    - page: Page number
    - page_size: Items per page
    """
    try:
        tenant = getattr(request.user, "tenant", None)
        if not tenant:
            return Response(
                {
                    "success": False,
                    "message": "User is not associated with any tenant. Please contact support.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get query parameters
        status_filter = request.GET.get("status")
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 20))

        # Build queryset
        queryset = Purchase.objects.filter(tenant=tenant)

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
            queryset = queryset.filter(created_at__date__gte=start_dt)

        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
            queryset = queryset.filter(created_at__date__lte=end_dt)

        # Pagination
        total_count = queryset.count()
        start_index = (page - 1) * page_size
        end_index = start_index + page_size

        purchases = queryset.order_by("-created_at")[start_index:end_index]

        # Serialize data
        purchase_data = []
        for purchase in purchases:
            purchase_data.append(
                {
                    "id": str(purchase.id),
                    "invoice_number": purchase.invoice_number,
                    "package_name": purchase.package.name,
                    "credits": purchase.credits,
                    "amount": float(purchase.amount),
                    "unit_price": float(purchase.unit_price),
                    "payment_method": purchase.get_payment_method_display(),
                    "status": purchase.status,
                    "created_at": purchase.created_at.isoformat(),
                    "completed_at": purchase.completed_at.isoformat()
                    if purchase.completed_at
                    else None,
                }
            )

        return Response(
            {
                "success": True,
                "data": {
                    "purchases": purchase_data,
                    "pagination": {
                        "page": page,
                        "page_size": page_size,
                        "total_count": total_count,
                        "total_pages": (total_count + page_size - 1) // page_size,
                        "has_next": end_index < total_count,
                        "has_previous": page > 1,
                    },
                },
            }
        )

    except Exception as e:
        logger.error(f"Purchase history error: {str(e)}")
        return Response(
            {
                "success": False,
                "message": "Failed to retrieve purchase history",
                "error": str(e),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def usage_statistics(request):
    """
    Get SMS usage statistics for billing.
    GET /api/billing/sms/usage/statistics/
    """
    try:
        tenant = getattr(request.user, "tenant", None)
        if not tenant:
            return Response(
                {
                    "success": False,
                    "message": "User is not associated with any tenant. Please contact support.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=7)

        # Get usage records
        total_usage = UsageRecord.objects.filter(tenant=tenant).aggregate(
            total_credits=Sum("credits_used"),
            total_cost=Sum("cost"),
        )

        monthly_usage = UsageRecord.objects.filter(
            tenant=tenant, created_at__gte=month_start
        ).aggregate(total_credits=Sum("credits_used"), total_cost=Sum("cost"))

        weekly_usage = UsageRecord.objects.filter(
            tenant=tenant, created_at__gte=week_start
        ).aggregate(total_credits=Sum("credits_used"), total_cost=Sum("cost"))

        # Get current balance
        balance = SMSBalance.objects.filter(tenant=tenant).first()
        current_balance = balance.credits if balance else 0

        # Get daily usage for the last 7 days
        daily_usage = []
        for i in range(7):
            day_start = now - timedelta(days=i+1)
            day_end = now - timedelta(days=i)
            day_usage = UsageRecord.objects.filter(
                tenant=tenant, 
                created_at__gte=day_start, 
                created_at__lt=day_end
            ).aggregate(
                total_credits=Sum("credits_used"), 
                total_cost=Sum("cost")
            )
            daily_usage.append({
                "date": day_start.strftime("%Y-%m-%d"),
                "credits": day_usage["total_credits"] or 0,
                "cost": float(day_usage["total_cost"] or 0),
            })

        return Response(
            {
                "success": True,
                "data": {
                    "current_balance": current_balance,
                    "total_usage": {
                        "credits": total_usage["total_credits"] or 0,
                        "cost": float(total_usage["total_cost"] or 0),
                        "period": "all_time"
                    },
                    "monthly_usage": {
                        "credits": monthly_usage["total_credits"] or 0,
                        "cost": float(monthly_usage["total_cost"] or 0),
                        "period": "monthly"
                    },
                    "weekly_usage": {
                        "credits": weekly_usage["total_credits"] or 0,
                        "cost": float(weekly_usage["total_cost"] or 0),
                        "period": "weekly"
                    },
                    "daily_usage": daily_usage,
                },
            }
        )

    except Exception as e:
        logger.error(f"Usage statistics error: {str(e)}")
        return Response(
            {
                "success": False,
                "message": "Failed to retrieve usage statistics",
                "error": str(e),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
