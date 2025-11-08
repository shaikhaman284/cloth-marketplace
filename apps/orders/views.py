from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from .models import Order
from .serializers import OrderCreateSerializer, OrderSerializer


class OrderPagination(PageNumberPagination):
    page_size = 20


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    """
    Create new order (Customer only)
    POST /api/orders/create

    Body:
    {
        "cart_items": [
            {
                "product_id": 1,
                "quantity": 2,
                "size": "M",
                "color": "Blue"
            }
        ],
        "delivery_name": "John Doe",
        "delivery_phone": "+919876543210",
        "delivery_address": "123 MG Road",
        "delivery_city": "Amravati",
        "delivery_pincode": "444601",
        "delivery_landmark": "Near Rajkamal Chowk"
    }
    """

    # Check if user is customer
    if request.user.user_type != 'customer':
        return Response({
            'success': False,
            'message': 'Only customers can place orders'
        }, status=status.HTTP_403_FORBIDDEN)

    serializer = OrderCreateSerializer(data=request.data, context={'request': request})

    if serializer.is_valid():
        order = serializer.save()
        order_serializer = OrderSerializer(order, context={'request': request})

        return Response({
            'success': True,
            'message': 'Order placed successfully',
            'order': order_serializer.data,
            'payment_info': {
                'method': 'Cash on Delivery',
                'amount_to_pay': f"₹{order.total_amount}",
                'cod_fee_included': f"₹{order.cod_fee}",
                'note': 'Pay cash when you receive your order'
            }
        }, status=status.HTTP_201_CREATED)

    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


# Add before my_orders view

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_statistics(request):
    """
    Get order statistics
    GET /api/orders/statistics

    For sellers: their shop's stats
    For customers: their order stats
    """

    user = request.user

    if user.user_type == 'seller':
        if not hasattr(user, 'shop'):
            return Response({
                'success': False,
                'message': 'No shop registered'
            }, status=status.HTTP_404_NOT_FOUND)

        orders = Order.objects.filter(shop=user.shop)

        # Calculate statistics
        from django.db.models import Sum, Count, Q
        from datetime import datetime, timedelta

        today = datetime.now().date()
        this_month = datetime.now().replace(day=1).date()

        stats = {
            'total_orders': orders.count(),
            'pending_orders': orders.filter(order_status__in=['placed', 'confirmed', 'shipped']).count(),
            'completed_orders': orders.filter(order_status='delivered').count(),
            'cancelled_orders': orders.filter(order_status='cancelled').count(),

            'today_orders': orders.filter(placed_at__date=today).count(),
            'today_revenue': orders.filter(
                placed_at__date=today,
                order_status='delivered'
            ).aggregate(Sum('seller_payout_amount'))['seller_payout_amount__sum'] or 0,

            'month_orders': orders.filter(placed_at__date__gte=this_month).count(),
            'month_revenue': orders.filter(
                placed_at__date__gte=this_month,
                order_status='delivered'
            ).aggregate(Sum('seller_payout_amount'))['seller_payout_amount__sum'] or 0,

            'total_earnings': orders.filter(
                order_status='delivered'
            ).aggregate(Sum('seller_payout_amount'))['seller_payout_amount__sum'] or 0,

            'pending_earnings': orders.filter(
                order_status__in=['confirmed', 'shipped']
            ).aggregate(Sum('seller_payout_amount'))['seller_payout_amount__sum'] or 0,
        }

        return Response({
            'success': True,
            'statistics': stats
        }, status=status.HTTP_200_OK)

    elif user.user_type == 'customer':
        orders = Order.objects.filter(customer=user)

        stats = {
            'total_orders': orders.count(),
            'active_orders': orders.filter(order_status__in=['placed', 'confirmed', 'shipped']).count(),
            'completed_orders': orders.filter(order_status='delivered').count(),
            'cancelled_orders': orders.filter(order_status='cancelled').count(),
        }

        return Response({
            'success': True,
            'statistics': stats
        }, status=status.HTTP_200_OK)

    return Response({
        'success': False,
        'message': 'Invalid user type'
    }, status=status.HTTP_403_FORBIDDEN)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_orders(request):
    """
    Get user's orders
    GET /api/orders/my-orders?status=placed&page=1

    For customers: their orders
    For sellers: orders for their shop
    """

    user = request.user

    if user.user_type == 'customer':
        orders = Order.objects.filter(customer=user)
    elif user.user_type == 'seller':
        if not hasattr(user, 'shop'):
            return Response({
                'success': False,
                'message': 'No shop registered'
            }, status=status.HTTP_404_NOT_FOUND)

        orders = Order.objects.filter(shop=user.shop)
    else:
        return Response({
            'success': False,
            'message': 'Invalid user type'
        }, status=status.HTTP_403_FORBIDDEN)

    # Filter by status
    order_status = request.GET.get('status')
    if order_status:
        orders = orders.filter(order_status=order_status)

    # Sort by newest first
    orders = orders.select_related('customer', 'shop').prefetch_related('items').order_by('-placed_at')

    # Pagination
    paginator = OrderPagination()
    paginated_orders = paginator.paginate_queryset(orders, request)

    serializer = OrderSerializer(paginated_orders, many=True, context={'request': request})

    return paginator.get_paginated_response({
        'success': True,
        'orders': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order_detail(request, order_number):
    """
    Get order details
    GET /api/orders/{order_number}
    """

    try:
        order = Order.objects.select_related('customer', 'shop').prefetch_related('items__product').get(
            order_number=order_number
        )

        # Check permission
        if request.user.user_type == 'customer' and order.customer != request.user:
            return Response({
                'success': False,
                'message': 'You don\'t have permission to view this order'
            }, status=status.HTTP_403_FORBIDDEN)

        if request.user.user_type == 'seller':
            if not hasattr(request.user, 'shop') or order.shop != request.user.shop:
                return Response({
                    'success': False,
                    'message': 'You don\'t have permission to view this order'
                }, status=status.HTTP_403_FORBIDDEN)

        serializer = OrderSerializer(order, context={'request': request})

        # Add extra info for sellers
        response_data = {
            'success': True,
            'order': serializer.data
        }

        if request.user.user_type == 'seller':
            response_data['seller_info'] = {
                'you_will_receive': f"₹{order.seller_payout_amount}",
                'commission_deducted': f"₹{order.commission_amount}",
                'cod_to_collect': f"₹{order.total_amount}",
                'note': f"Collect ₹{order.total_amount} from customer. Keep ₹{order.seller_payout_amount}. Pay ₹{order.cod_fee} COD fee."
            }

        return Response(response_data, status=status.HTTP_200_OK)

    except Order.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Order not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_order_status(request, order_number):
    """
    Update order status (Seller only)
    PATCH /api/orders/{order_number}/status

    Body:
    {
        "new_status": "confirmed" | "shipped" | "delivered"
    }

    Allowed transitions:
    - placed → confirmed
    - confirmed → shipped
    - shipped → delivered
    """

    # Only sellers can update status
    if request.user.user_type != 'seller':
        return Response({
            'success': False,
            'message': 'Only sellers can update order status'
        }, status=status.HTTP_403_FORBIDDEN)

    try:
        order = Order.objects.select_related('shop').get(
            order_number=order_number,
            shop=request.user.shop
        )
    except Order.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Order not found or you don\'t have permission'
        }, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get('new_status')

    if not new_status:
        return Response({
            'success': False,
            'message': 'new_status is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Validate status transitions
    current_status = order.order_status

    valid_transitions = {
        'placed': ['confirmed', 'cancelled'],
        'confirmed': ['shipped', 'cancelled'],
        'shipped': ['delivered'],
        'delivered': [],
        'cancelled': []
    }

    if new_status not in valid_transitions.get(current_status, []):
        return Response({
            'success': False,
            'message': f'Cannot change status from {current_status} to {new_status}'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Update status with timestamp
    order.order_status = new_status

    if new_status == 'confirmed':
        order.confirmed_at = timezone.now()
    elif new_status == 'shipped':
        order.shipped_at = timezone.now()
    elif new_status == 'delivered':
        order.delivered_at = timezone.now()
        # Mark COD as collected when delivered
        if order.payment_method == 'cod':
            order.payment_status = 'cod_collected'
    elif new_status == 'cancelled':
        order.cancelled_at = timezone.now()
        order.cancellation_reason = request.data.get('reason', 'Cancelled by seller')

        # Restore stock for cancelled orders
        for item in order.items.all():
            if item.product:
                item.product.stock_quantity += item.quantity
                item.product.save(update_fields=['stock_quantity'])

    order.save()

    serializer = OrderSerializer(order, context={'request': request})

    # Prepare response message
    messages = {
        'confirmed': 'Order confirmed successfully',
        'shipped': 'Order marked as shipped',
        'delivered': 'Order delivered successfully',
        'cancelled': 'Order cancelled'
    }

    response_data = {
        'success': True,
        'message': messages.get(new_status, 'Status updated'),
        'order': serializer.data
    }

    # Add seller instructions for COD
    if new_status == 'delivered' and order.payment_method == 'cod':
        response_data['cod_instructions'] = {
            'collected_from_customer': f"₹{order.total_amount}",
            'your_earnings': f"₹{order.seller_payout_amount}",
            'cod_fee_to_pay': f"₹{order.cod_fee}",
            'platform_commission': f"₹{order.commission_amount}",
            'note': f"You collected ₹{order.total_amount}. Keep ₹{order.seller_payout_amount}. Pay ₹{order.cod_fee} COD fee to platform."
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_order(request, order_number):
    """
    Cancel order (Customer can cancel if not confirmed yet)
    POST /api/orders/{order_number}/cancel

    Body:
    {
        "reason": "Changed my mind"
    }
    """

    try:
        order = Order.objects.get(order_number=order_number)

        # Check permission
        if request.user.user_type == 'customer' and order.customer != request.user:
            return Response({
                'success': False,
                'message': 'You don\'t have permission to cancel this order'
            }, status=status.HTTP_403_FORBIDDEN)

        # Can only cancel if not confirmed yet
        if order.order_status not in ['placed']:
            return Response({
                'success': False,
                'message': f'Cannot cancel order with status: {order.order_status}'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Cancel order
        order.order_status = 'cancelled'
        order.cancelled_at = timezone.now()
        order.cancellation_reason = request.data.get('reason', 'Cancelled by customer')
        order.save()

        # Restore stock
        for item in order.items.all():
            if item.product:
                item.product.stock_quantity += item.quantity
                item.product.save(update_fields=['stock_quantity'])

        return Response({
            'success': True,
            'message': 'Order cancelled successfully'
        }, status=status.HTTP_200_OK)

    except Order.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Order not found'
        }, status=status.HTTP_404_NOT_FOUND)