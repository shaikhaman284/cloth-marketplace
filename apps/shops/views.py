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