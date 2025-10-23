"""
Billing history views for comprehensive billing data.
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import (
    Purchase, PaymentTransaction, UsageRecord, SMSBalance,
    CustomSMSPurchase, BillingPlan, Subscription
)
from .serializers import (
    PurchaseSerializer, PaymentTransactionSerializer, UsageRecordSerializer,
    CustomSMSPurchaseSerializer
)


class BillingHistoryView(generics.ListAPIView):
    """
    Get comprehensive billing history for the tenant.
    Includes purchases, payments, usage, and custom purchases.
    """
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get all billing-related records for the tenant."""
        # Handle Swagger schema generation with AnonymousUser
        if not self.request.user.is_authenticated:
            return Purchase.objects.none()

        tenant = getattr(self.request.user, 'tenant', None)
        if not tenant:
            return Purchase.objects.none()

        # Get all purchases for the tenant
        return Purchase.objects.filter(tenant=tenant).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        """Return comprehensive billing history."""
        try:
            tenant = getattr(request.user, 'tenant', None)
            if not tenant:
                return Response(
                    {
                        'success': False,
                        'message': 'User is not associated with any tenant.',
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Get date range filters
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')

            # Build date filter
            date_filter = Q()
            if start_date:
                try:
                    start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
                    date_filter &= Q(created_at__date__gte=start_dt)
                except ValueError:
                    pass
            if end_date:
                try:
                    end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
                    date_filter &= Q(created_at__date__lte=end_dt)
                except ValueError:
                    pass

            # Get purchases
            purchases = Purchase.objects.filter(tenant=tenant).filter(date_filter).order_by('-created_at')
            purchase_data = PurchaseSerializer(purchases, many=True).data

            # Get payment transactions
            payments = PaymentTransaction.objects.filter(tenant=tenant).filter(date_filter).order_by('-created_at')
            payment_data = PaymentTransactionSerializer(payments, many=True).data

            # Get usage records
            usage_records = UsageRecord.objects.filter(tenant=tenant).filter(date_filter).order_by('-created_at')
            usage_data = UsageRecordSerializer(usage_records, many=True).data

            # Get custom SMS purchases
            custom_purchases = CustomSMSPurchase.objects.filter(tenant=tenant).filter(date_filter).order_by('-created_at')
            custom_purchase_data = CustomSMSPurchaseSerializer(custom_purchases, many=True).data

            # Calculate summary statistics
            total_purchased = purchases.aggregate(total=Sum('amount'))['total'] or 0
            total_credits_purchased = purchases.aggregate(total=Sum('credits'))['total'] or 0
            total_usage_cost = usage_records.aggregate(total=Sum('cost'))['total'] or 0
            total_credits_used = usage_records.aggregate(total=Sum('credits_used'))['total'] or 0

            # Get current balance
            sms_balance, _ = SMSBalance.objects.get_or_create(tenant=tenant)

            return Response({
                'success': True,
                'data': {
                    'summary': {
                        'total_purchased': float(total_purchased),
                        'total_credits_purchased': total_credits_purchased,
                        'total_usage_cost': float(total_usage_cost),
                        'total_credits_used': total_credits_used,
                        'current_balance': sms_balance.credits,
                        'total_purchases': purchases.count(),
                        'total_payments': payments.count(),
                        'total_usage_records': usage_records.count(),
                    },
                    'purchases': purchase_data,
                    'payments': payment_data,
                    'usage_records': usage_data,
                    'custom_purchases': custom_purchase_data,
                }
            })

        except Exception as e:
            return Response(
                {
                    'success': False,
                    'message': 'Failed to retrieve billing history',
                    'error': str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@swagger_auto_schema(
    method='get',
    operation_description="Get billing history summary with statistics and charts data.",
    manual_parameters=[
        openapi.Parameter(
            'start_date',
            openapi.IN_QUERY,
            description="Start date (YYYY-MM-DD)",
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATE
        ),
        openapi.Parameter(
            'end_date',
            openapi.IN_QUERY,
            description="End date (YYYY-MM-DD)",
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATE
        ),
        openapi.Parameter(
            'period',
            openapi.IN_QUERY,
            description="Time period (7d, 30d, 90d, 1y)",
            type=openapi.TYPE_STRING
        ),
    ],
    responses={
        200: openapi.Response(
            description="Success",
            examples={
                "application/json": {
                    "success": True,
                    "data": {
                        "summary": {
                            "total_purchased": 150000.00,
                            "total_credits_purchased": 5000,
                            "total_usage_cost": 125000.00,
                            "total_credits_used": 4500,
                            "current_balance": 500,
                            "total_purchases": 3,
                            "total_payments": 3,
                            "total_usage_records": 45
                        },
                        "charts": {
                            "monthly_usage": [
                                {"month": "2025-01", "credits": 1000, "cost": 25000},
                                {"month": "2025-02", "credits": 1200, "cost": 30000}
                            ],
                            "payment_methods": [
                                {"method": "mpesa", "count": 2, "amount": 100000},
                                {"method": "tigopesa", "count": 1, "amount": 50000}
                            ]
                        }
                    }
                }
            }
        ),
        400: "Invalid request parameters",
        500: "Internal Server Error",
    },
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def billing_history_summary(request):
    """
    Get billing history summary with statistics and charts data.
    GET /api/billing/history/summary/
    """
    try:
        tenant = getattr(request.user, 'tenant', None)
        if not tenant:
            return Response(
                {
                    'success': False,
                    'message': 'User is not associated with any tenant.',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get period filter
        period = request.query_params.get('period', '30d')
        end_date = timezone.now().date()

        if period == '7d':
            start_date = end_date - timedelta(days=7)
        elif period == '30d':
            start_date = end_date - timedelta(days=30)
        elif period == '90d':
            start_date = end_date - timedelta(days=90)
        elif period == '1y':
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=30)

        # Get purchases in period
        purchases = Purchase.objects.filter(
            tenant=tenant,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )

        # Get usage records in period
        usage_records = UsageRecord.objects.filter(
            tenant=tenant,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )

        # Get payments in period
        payments = PaymentTransaction.objects.filter(
            tenant=tenant,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )

        # Calculate summary statistics
        total_purchased = purchases.aggregate(total=Sum('amount'))['total'] or 0
        total_credits_purchased = purchases.aggregate(total=Sum('credits'))['total'] or 0
        total_usage_cost = usage_records.aggregate(total=Sum('cost'))['total'] or 0
        total_credits_used = usage_records.aggregate(total=Sum('credits_used'))['total'] or 0

        # Get current balance
        sms_balance, _ = SMSBalance.objects.get_or_create(tenant=tenant)

        # Generate monthly usage chart data
        monthly_usage = []
        current_date = start_date
        while current_date <= end_date:
            month_start = current_date.replace(day=1)
            if current_date.month == 12:
                month_end = current_date.replace(year=current_date.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                month_end = current_date.replace(month=current_date.month + 1, day=1) - timedelta(days=1)

            month_usage = usage_records.filter(
                created_at__date__gte=month_start,
                created_at__date__lte=month_end
            ).aggregate(
                credits=Sum('credits_used'),
                cost=Sum('cost')
            )

            monthly_usage.append({
                'month': month_start.strftime('%Y-%m'),
                'credits': month_usage['credits'] or 0,
                'cost': float(month_usage['cost'] or 0)
            })

            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1, day=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1, day=1)

        # Generate payment methods chart data
        payment_methods = payments.values('payment_method').annotate(
            count=Count('id'),
            amount=Sum('amount')
        ).order_by('-amount')

        payment_methods_data = [
            {
                'method': item['payment_method'],
                'count': item['count'],
                'amount': float(item['amount'] or 0)
            }
            for item in payment_methods
        ]

        return Response({
            'success': True,
            'data': {
                'summary': {
                    'total_purchased': float(total_purchased),
                    'total_credits_purchased': total_credits_purchased,
                    'total_usage_cost': float(total_usage_cost),
                    'total_credits_used': total_credits_used,
                    'current_balance': sms_balance.credits,
                    'total_purchases': purchases.count(),
                    'total_payments': payments.count(),
                    'total_usage_records': usage_records.count(),
                    'period': period,
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                },
                'charts': {
                    'monthly_usage': monthly_usage,
                    'payment_methods': payment_methods_data,
                }
            }
        })

    except Exception as e:
        return Response(
            {
                'success': False,
                'message': 'Failed to retrieve billing history summary',
                'error': str(e),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@swagger_auto_schema(
    method='get',
    operation_description="Get detailed purchase history for the tenant.",
    manual_parameters=[
        openapi.Parameter(
            'status',
            openapi.IN_QUERY,
            description="Filter by purchase status",
            type=openapi.TYPE_STRING,
            enum=['pending', 'completed', 'failed', 'cancelled', 'expired', 'refunded']
        ),
        openapi.Parameter(
            'start_date',
            openapi.IN_QUERY,
            description="Start date (YYYY-MM-DD)",
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATE
        ),
        openapi.Parameter(
            'end_date',
            openapi.IN_QUERY,
            description="End date (YYYY-MM-DD)",
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATE
        ),
        openapi.Parameter(
            'page',
            openapi.IN_QUERY,
            description="Page number",
            type=openapi.TYPE_INTEGER,
            default=1
        ),
        openapi.Parameter(
            'page_size',
            openapi.IN_QUERY,
            description="Number of items per page",
            type=openapi.TYPE_INTEGER,
            default=20
        ),
    ],
    responses={
        200: openapi.Response(
            description="Success",
            examples={
                "application/json": {
                    "success": True,
                    "data": {
                        "purchases": [
                            {
                                "id": "uuid",
                                "invoice_number": "INV-001",
                                "package_name": "Standard Package",
                                "amount": 50000.00,
                                "credits": 2000,
                                "status": "completed",
                                "created_at": "2025-01-15T10:30:00Z"
                            }
                        ],
                        "pagination": {
                            "count": 10,
                            "next": None,
                            "previous": None,
                            "page": 1,
                            "page_size": 20
                        }
                    }
                }
            }
        ),
        400: "Invalid request parameters",
        500: "Internal Server Error",
    },
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def purchase_history_detailed(request):
    """
    Get detailed purchase history with pagination and filtering.
    GET /api/billing/history/purchases/
    """
    try:
        tenant = getattr(request.user, 'tenant', None)
        if not tenant:
            return Response(
                {
                    'success': False,
                    'message': 'User is not associated with any tenant.',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get filters
        status_filter = request.query_params.get('status')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))

        # Build query
        queryset = Purchase.objects.filter(tenant=tenant).select_related('package')

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        if start_date:
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__gte=start_dt)
            except ValueError:
                pass

        if end_date:
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__lte=end_dt)
            except ValueError:
                pass

        # Order by creation date
        queryset = queryset.order_by('-created_at')

        # Pagination
        total_count = queryset.count()
        start_index = (page - 1) * page_size
        end_index = start_index + page_size

        purchases = queryset[start_index:end_index]
        purchase_data = PurchaseSerializer(purchases, many=True).data

        # Calculate pagination info
        has_next = end_index < total_count
        has_previous = page > 1

        return Response({
            'success': True,
            'data': {
                'purchases': purchase_data,
                'pagination': {
                    'count': total_count,
                    'next': f"?page={page + 1}&page_size={page_size}" if has_next else None,
                    'previous': f"?page={page - 1}&page_size={page_size}" if has_previous else None,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': (total_count + page_size - 1) // page_size
                }
            }
        })

    except Exception as e:
        return Response(
            {
                'success': False,
                'message': 'Failed to retrieve purchase history',
                'error': str(e),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@swagger_auto_schema(
    method='get',
    operation_description="Get payment transaction history for the tenant.",
    manual_parameters=[
        openapi.Parameter(
            'status',
            openapi.IN_QUERY,
            description="Filter by payment status",
            type=openapi.TYPE_STRING,
            enum=['pending', 'processing', 'completed', 'failed', 'cancelled', 'expired', 'refunded']
        ),
        openapi.Parameter(
            'payment_method',
            openapi.IN_QUERY,
            description="Filter by payment method",
            type=openapi.TYPE_STRING,
            enum=['zenopay_mobile_money', 'mpesa', 'tigopesa', 'airtelmoney', 'bank_transfer', 'credit_card']
        ),
        openapi.Parameter(
            'start_date',
            openapi.IN_QUERY,
            description="Start date (YYYY-MM-DD)",
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATE
        ),
        openapi.Parameter(
            'end_date',
            openapi.IN_QUERY,
            description="End date (YYYY-MM-DD)",
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATE
        ),
        openapi.Parameter(
            'page',
            openapi.IN_QUERY,
            description="Page number",
            type=openapi.TYPE_INTEGER,
            default=1
        ),
        openapi.Parameter(
            'page_size',
            openapi.IN_QUERY,
            description="Number of items per page",
            type=openapi.TYPE_INTEGER,
            default=20
        ),
    ],
    responses={
        200: openapi.Response(
            description="Success",
            examples={
                "application/json": {
                    "success": True,
                    "data": {
                        "transactions": [
                            {
                                "id": "uuid",
                                "order_id": "ORD-001",
                                "amount": 50000.00,
                                "currency": "TZS",
                                "payment_method": "mpesa",
                                "status": "completed",
                                "created_at": "2025-01-15T10:30:00Z"
                            }
                        ],
                        "pagination": {
                            "count": 10,
                            "next": None,
                            "previous": None,
                            "page": 1,
                            "page_size": 20
                        }
                    }
                }
            }
        ),
        400: "Invalid request parameters",
        500: "Internal Server Error",
    },
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_history_detailed(request):
    """
    Get detailed payment transaction history with pagination and filtering.
    GET /api/billing/history/payments/
    """
    try:
        tenant = getattr(request.user, 'tenant', None)
        if not tenant:
            return Response(
                {
                    'success': False,
                    'message': 'User is not associated with any tenant.',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get filters
        status_filter = request.query_params.get('status')
        payment_method = request.query_params.get('payment_method')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))

        # Build query
        queryset = PaymentTransaction.objects.filter(tenant=tenant)

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)

        if start_date:
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__gte=start_dt)
            except ValueError:
                pass

        if end_date:
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__lte=end_dt)
            except ValueError:
                pass

        # Order by creation date
        queryset = queryset.order_by('-created_at')

        # Pagination
        total_count = queryset.count()
        start_index = (page - 1) * page_size
        end_index = start_index + page_size

        transactions = queryset[start_index:end_index]
        transaction_data = PaymentTransactionSerializer(transactions, many=True).data

        # Calculate pagination info
        has_next = end_index < total_count
        has_previous = page > 1

        return Response({
            'success': True,
            'data': {
                'transactions': transaction_data,
                'pagination': {
                    'count': total_count,
                    'next': f"?page={page + 1}&page_size={page_size}" if has_next else None,
                    'previous': f"?page={page - 1}&page_size={page_size}" if has_previous else None,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': (total_count + page_size - 1) // page_size
                }
            }
        })

    except Exception as e:
        return Response(
            {
                'success': False,
                'message': 'Failed to retrieve payment history',
                'error': str(e),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@swagger_auto_schema(
    method='get',
    operation_description="Get usage history for the tenant.",
    manual_parameters=[
        openapi.Parameter(
            'start_date',
            openapi.IN_QUERY,
            description="Start date (YYYY-MM-DD)",
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATE
        ),
        openapi.Parameter(
            'end_date',
            openapi.IN_QUERY,
            description="End date (YYYY-MM-DD)",
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATE
        ),
        openapi.Parameter(
            'page',
            openapi.IN_QUERY,
            description="Page number",
            type=openapi.TYPE_INTEGER,
            default=1
        ),
        openapi.Parameter(
            'page_size',
            openapi.IN_QUERY,
            description="Number of items per page",
            type=openapi.TYPE_INTEGER,
            default=20
        ),
    ],
    responses={
        200: openapi.Response(
            description="Success",
            examples={
                "application/json": {
                    "success": True,
                    "data": {
                        "usage_records": [
                            {
                                "id": "uuid",
                                "credits_used": 1,
                                "cost": 25.00,
                                "created_at": "2025-01-15T10:30:00Z"
                            }
                        ],
                        "pagination": {
                            "count": 100,
                            "next": "?page=2&page_size=20",
                            "previous": None,
                            "page": 1,
                            "page_size": 20
                        }
                    }
                }
            }
        ),
        400: "Invalid request parameters",
        500: "Internal Server Error",
    },
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def usage_history_detailed(request):
    """
    Get detailed usage history with pagination and filtering.
    GET /api/billing/history/usage/
    """
    try:
        tenant = getattr(request.user, 'tenant', None)
        if not tenant:
            return Response(
                {
                    'success': False,
                    'message': 'User is not associated with any tenant.',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get filters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))

        # Build query
        queryset = UsageRecord.objects.filter(tenant=tenant)

        if start_date:
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__gte=start_dt)
            except ValueError:
                pass

        if end_date:
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__lte=end_dt)
            except ValueError:
                pass

        # Order by creation date
        queryset = queryset.order_by('-created_at')

        # Pagination
        total_count = queryset.count()
        start_index = (page - 1) * page_size
        end_index = start_index + page_size

        usage_records = queryset[start_index:end_index]
        usage_data = UsageRecordSerializer(usage_records, many=True).data

        # Calculate pagination info
        has_next = end_index < total_count
        has_previous = page > 1

        return Response({
            'success': True,
            'data': {
                'usage_records': usage_data,
                'pagination': {
                    'count': total_count,
                    'next': f"?page={page + 1}&page_size={page_size}" if has_next else None,
                    'previous': f"?page={page - 1}&page_size={page_size}" if has_previous else None,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': (total_count + page_size - 1) // page_size
                }
            }
        })

    except Exception as e:
        return Response(
            {
                'success': False,
                'message': 'Failed to retrieve usage history',
                'error': str(e),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@swagger_auto_schema(
    method='get',
    operation_description="Get comprehensive transaction history including all payment types.",
    manual_parameters=[
        openapi.Parameter(
            'page',
            openapi.IN_QUERY,
            description="Page number",
            type=openapi.TYPE_INTEGER,
            default=1
        ),
        openapi.Parameter(
            'page_size',
            openapi.IN_QUERY,
            description="Number of items per page",
            type=openapi.TYPE_INTEGER,
            default=20
        ),
        openapi.Parameter(
            'status',
            openapi.IN_QUERY,
            description="Filter by transaction status",
            type=openapi.TYPE_STRING
        ),
        openapi.Parameter(
            'transaction_type',
            openapi.IN_QUERY,
            description="Filter by transaction type (purchase, payment, custom)",
            type=openapi.TYPE_STRING
        ),
    ],
    responses={
        200: "Transaction history retrieved successfully",
        400: "Invalid request parameters",
        500: "Internal Server Error",
    },
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def comprehensive_transaction_history(request):
    """
    Get comprehensive transaction history including purchases, payments, and custom SMS purchases.
    GET /api/billing/history/comprehensive/
    """
    try:
        tenant = getattr(request.user, 'tenant', None)
        if not tenant:
            return Response(
                {
                    'success': False,
                    'message': 'User is not associated with any tenant.',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get filters
        status_filter = request.query_params.get('status')
        transaction_type = request.query_params.get('transaction_type')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))

        # Collect all transaction types
        transactions = []

        # 1. Regular Purchases
        purchases = Purchase.objects.filter(tenant=tenant).select_related('package')
        if status_filter:
            purchases = purchases.filter(status=status_filter)

        for purchase in purchases:
            transactions.append({
                'id': str(purchase.id),
                'type': 'purchase',
                'type_display': 'SMS Package Purchase',
                'invoice_number': purchase.invoice_number,
                'amount': float(purchase.amount),
                'currency': 'TZS',
                'status': purchase.status,
                'status_display': purchase.get_status_display(),
                'payment_method': purchase.payment_method,
                'payment_method_display': purchase.get_payment_method_display(),
                'credits': purchase.credits,
                'package_name': purchase.package.name if purchase.package else 'Unknown Package',
                'unit_price': float(purchase.unit_price),
                'created_at': purchase.created_at,
                'completed_at': purchase.completed_at,
                'description': f"Purchased {purchase.credits} SMS credits from {purchase.package.name if purchase.package else 'Unknown Package'}",
                'icon': '📦',
                'color': 'blue'
            })

        # 2. Payment Transactions (standalone only - exclude ones that belong to a purchase or custom purchase)
        from billing.models import PaymentTransaction
        payment_transactions = (
            PaymentTransaction.objects
            .filter(tenant=tenant, purchase__isnull=True, custom_sms_purchase__isnull=True)
        )
        if status_filter:
            payment_transactions = payment_transactions.filter(status=status_filter)

        for pt in payment_transactions:
            transactions.append({
                'id': str(pt.id),
                'type': 'payment',
                'type_display': 'Payment Transaction',
                'invoice_number': pt.invoice_number,
                'amount': float(pt.amount),
                'currency': pt.currency,
                'status': pt.status,
                'status_display': pt.get_status_display(),
                'payment_method': pt.payment_method,
                'payment_method_display': pt.get_payment_method_display(),
                'credits': None,
                'package_name': None,
                'unit_price': None,
                'created_at': pt.created_at,
                'completed_at': pt.completed_at,
                'description': f"Payment of {pt.amount} {pt.currency} via {pt.get_payment_method_display()}",
                'buyer_name': pt.buyer_name,
                'buyer_email': pt.buyer_email,
                'buyer_phone': pt.buyer_phone,
                'icon': '💳',
                'color': 'green'
            })

        # 3. Custom SMS Purchases (combine with their payment data into a single entry)
        from billing.models import CustomSMSPurchase
        custom_purchases = CustomSMSPurchase.objects.filter(tenant=tenant)
        if status_filter:
            custom_purchases = custom_purchases.filter(status=status_filter)

        for csp in custom_purchases:
            # Prefer payment status if available (so the row reflects real payment progress)
            combined_status = csp.status
            payment_method_display = 'Custom Purchase'
            payment_method = 'custom'
            invoice_number = f"CSP-{str(csp.id)[:8].upper()}"
            buyer_name = None
            buyer_email = None
            buyer_phone = None
            order_id = None

            if getattr(csp, 'payment_transaction', None):
                pt = csp.payment_transaction
                invoice_number = pt.invoice_number or invoice_number
                combined_status = pt.status or combined_status
                payment_method = pt.payment_method
                payment_method_display = pt.get_payment_method_display()
                buyer_name = pt.buyer_name
                buyer_email = pt.buyer_email
                buyer_phone = pt.buyer_phone
                order_id = pt.order_id

            transactions.append({
                'id': str(csp.id),
                'type': 'custom',
                'type_display': 'Custom SMS Purchase',
                'invoice_number': invoice_number,
                'amount': float(csp.total_price),
                'currency': 'TZS',
                'status': combined_status,
                'status_display': combined_status.title() if isinstance(combined_status, str) else str(combined_status),
                'payment_method': payment_method,
                'payment_method_display': payment_method_display,
                'credits': csp.credits,
                'package_name': f"Custom ({csp.active_tier})",
                'unit_price': float(csp.unit_price),
                'created_at': csp.created_at,
                'completed_at': csp.completed_at,
                'description': f"Custom purchase of {csp.credits} SMS credits at {csp.unit_price} TZS each",
                'tier_info': {
                    'active_tier': csp.active_tier,
                    'min_credits': csp.tier_min_credits,
                    'max_credits': csp.tier_max_credits
                },
                'buyer_name': buyer_name,
                'buyer_email': buyer_email,
                'buyer_phone': buyer_phone,
                'order_id': order_id,
                'icon': '⚙️',
                'color': 'purple'
            })

        # Filter by transaction type if specified
        if transaction_type:
            transactions = [t for t in transactions if t['type'] == transaction_type]

        # Sort by creation date (newest first)
        transactions.sort(key=lambda x: x['created_at'], reverse=True)

        # Ensure all transactions have consistent status mapping
        for transaction in transactions:
            # Map any "processing" status to "pending" for consistency
            if transaction['status'] == 'processing':
                transaction['status'] = 'pending'
                transaction['status_display'] = 'Pending'

        # Pagination
        total_count = len(transactions)
        start_index = (page - 1) * page_size
        end_index = start_index + page_size

        paginated_transactions = transactions[start_index:end_index]

        # Calculate pagination info
        has_next = end_index < total_count
        has_previous = page > 1

        # Calculate summary statistics
        total_amount = sum(t['amount'] for t in transactions if t['status'] == 'completed')
        total_credits = sum(t['credits'] for t in transactions if t['credits'] and t['status'] == 'completed')

        return Response({
            'success': True,
            'data': {
                'transactions': paginated_transactions,
                'summary': {
                    'total_transactions': total_count,
                    'total_amount': total_amount,
                    'total_credits': total_credits,
                    'currency': 'TZS'
                },
                'pagination': {
                    'count': total_count,
                    'next': f"?page={page + 1}&page_size={page_size}" if has_next else None,
                    'previous': f"?page={page - 1}&page_size={page_size}" if has_previous else None,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': (total_count + page_size - 1) // page_size
                }
            }
        })

    except Exception as e:
        return Response(
            {
                'success': False,
                'message': 'Failed to retrieve comprehensive transaction history',
                'error': str(e),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
