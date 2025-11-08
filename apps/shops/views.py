from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import Shop
from .serializers import ShopRegistrationSerializer, ShopSerializer
from config.firebase_config import upload_to_firebase_storage
from django.utils import timezone


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_shop(request):
    """
    Register a new shop (Seller only)
    POST /api/shops/register
    Body (form-data):
    - shop_name
    - business_address
    - city (must be Amravati)
    - pincode
    - owner_contact_number
    - gst_number (optional)
    - shop_image (file, optional)
    """

    # Check if user is seller
    if request.user.user_type != 'seller':
        return Response({
            'success': False,
            'message': 'Only sellers can register shops'
        }, status=status.HTTP_403_FORBIDDEN)

    # Check if seller already has a shop
    if hasattr(request.user, 'shop'):
        return Response({
            'success': False,
            'message': 'You already have a registered shop'
        }, status=status.HTTP_400_BAD_REQUEST)

    serializer = ShopRegistrationSerializer(data=request.data)

    if serializer.is_valid():
        # Create shop
        shop = serializer.save(owner=request.user)

        # Upload shop image if provided
        if 'shop_image' in request.FILES:
            shop_image = request.FILES['shop_image']
            image_path = f"shops/{shop.id}/{shop_image.name}"
            image_url = upload_to_firebase_storage(shop_image, image_path)

            if image_url:
                shop.shop_image_url = image_url
                shop.save()

        return Response({
            'success': True,
            'message': 'Shop registered successfully. Waiting for approval.',
            'shop': ShopSerializer(shop).data
        }, status=status.HTTP_201_CREATED)

    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_shop(request):
    """
    Get seller's shop details
    GET /api/shops/me
    """
    if request.user.user_type != 'seller':
        return Response({
            'success': False,
            'message': 'Only sellers can access this'
        }, status=status.HTTP_403_FORBIDDEN)

    try:
        shop = request.user.shop
        return Response({
            'success': True,
            'shop': ShopSerializer(shop).data
        }, status=status.HTTP_200_OK)

    except Shop.DoesNotExist:
        return Response({
            'success': False,
            'message': 'No shop registered yet'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def list_approved_shops(request):
    """
    List all approved shops (Public - for customers)
    GET /api/shops/approved
    Query params: city (optional, default: Amravati)
    """
    city = request.GET.get('city', 'Amravati')

    shops = Shop.objects.filter(
        is_approved=True,
        is_active=True,
        city__iexact=city  # Case-insensitive
    ).select_related('owner')

    serializer = ShopSerializer(shops, many=True)

    return Response({
        'success': True,
        'count': shops.count(),
        'city': city,
        'shops': serializer.data
    }, status=status.HTTP_200_OK)


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Count
from datetime import datetime, timedelta
from apps.orders.models import Order
from apps.products.models import Product


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def seller_dashboard(request):
    """
    Get seller dashboard statistics
    GET /api/sellers/dashboard

    Returns:
    - Product stats
    - Order stats
    - Earnings (delivered orders)
    - Recent orders
    """

    # Check if user is seller
    if request.user.user_type != 'seller':
        return Response({
            'success': False,
            'message': 'Only sellers can access dashboard'
        }, status=status.HTTP_403_FORBIDDEN)

    # Check if seller has shop
    if not hasattr(request.user, 'shop'):
        return Response({
            'success': False,
            'message': 'No shop registered'
        }, status=status.HTTP_404_NOT_FOUND)

    shop = request.user.shop

    # Date ranges
    today = datetime.now().date()
    this_month = datetime.now().replace(day=1).date()

    # Product statistics
    products = Product.objects.filter(shop=shop)
    product_stats = {
        'total_products': products.count(),
        'active_products': products.filter(is_active=True).count(),
        'out_of_stock': products.filter(stock_quantity=0, is_active=True).count(),
    }

    # Order statistics
    orders = Order.objects.filter(shop=shop)

    order_stats = {
        'total_orders': orders.count(),
        'pending_orders': orders.filter(order_status='placed').count(),
        'confirmed_orders': orders.filter(order_status='confirmed').count(),
        'shipped_orders': orders.filter(order_status='shipped').count(),
        'delivered_orders': orders.filter(order_status='delivered').count(),
        'cancelled_orders': orders.filter(order_status='cancelled').count(),

        # Today's stats
        'today_orders': orders.filter(placed_at__date=today).count(),
        'today_revenue': orders.filter(
            placed_at__date=today,
            order_status='delivered'
        ).aggregate(total=Sum('seller_payout_amount'))['total'] or 0,

        # This month
        'month_orders': orders.filter(placed_at__date__gte=this_month).count(),
        'month_revenue': orders.filter(
            placed_at__date__gte=this_month,
            order_status='delivered'
        ).aggregate(total=Sum('seller_payout_amount'))['total'] or 0,
    }

    # Earnings statistics
    earnings = {
        'total_earned': orders.filter(
            order_status='delivered'
        ).aggregate(total=Sum('seller_payout_amount'))['total'] or 0,

        'pending_earnings': orders.filter(
            order_status__in=['confirmed', 'shipped']
        ).aggregate(total=Sum('seller_payout_amount'))['total'] or 0,

        'total_commission_paid': orders.filter(
            order_status='delivered'
        ).aggregate(total=Sum('commission_amount'))['total'] or 0,
    }

    # Recent orders
    from apps.orders.serializers import OrderSerializer
    recent_orders = orders.select_related('customer').prefetch_related('items').order_by('-placed_at')[:5]
    recent_orders_data = OrderSerializer(recent_orders, many=True, context={'request': request}).data

    # Shop info
    shop_info = {
        'shop_name': shop.shop_name,
        'city': shop.city,
        'commission_rate': f"{shop.commission_rate}%",
        'is_approved': shop.is_approved,
        'approval_status': shop.approval_status,
    }

    return Response({
        'success': True,
        'shop_info': shop_info,
        'product_stats': product_stats,
        'order_stats': order_stats,
        'earnings': earnings,
        'recent_orders': recent_orders_data,
        'pricing_info': {
            'note': f"You earn base prices. Commission ({shop.commission_rate}%) is added to customer's price.",
            'example': {
                'your_price': '₹1000',
                'customer_pays': f"₹{1000 * (1 + float(shop.commission_rate) / 100)}",
                'platform_commission': f"₹{1000 * float(shop.commission_rate) / 100}"
            }
        }
    }, status=status.HTTP_200_OK)