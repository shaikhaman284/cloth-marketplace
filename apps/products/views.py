from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from .models import Category, Product, ProductImage
from .serializers import (CategorySerializer, ProductCreateSerializer,
                          ProductSerializer, ProductDetailSerializer)
from config.firebase_config import upload_to_firebase_storage



class ProductPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_product(request):
    """
    Create new product (Seller only)
    POST /api/products
    Body:
    - category (id)
    - name
    - description (optional)
    - base_price (what seller receives)
    - stock_quantity
    - sizes (array)
    - colors (array)
    - material (optional)
    - brand (optional)
    """

    # Check if user is seller
    if request.user.user_type != 'seller':
        return Response({
            'success': False,
            'message': 'Only sellers can create products'
        }, status=status.HTTP_403_FORBIDDEN)

    # Check if seller has approved shop
    if not hasattr(request.user, 'shop') or not request.user.shop.is_approved:
        return Response({
            'success': False,
            'message': 'Your shop must be approved first'
        }, status=status.HTTP_403_FORBIDDEN)

    serializer = ProductCreateSerializer(data=request.data, context={'request': request})

    if serializer.is_valid():
        product = serializer.save()

        return Response({
            'success': True,
            'message': 'Product created successfully',
            'product': ProductSerializer(product, context={'request': request}).data,
            'pricing_info': {
                'your_price': f"₹{product.base_price}",
                'commission': f"{product.commission_rate}%",
                'customer_pays': f"₹{product.display_price}",
                'note': "You receive the base price. Commission is added to customer's price."
            }
        }, status=status.HTTP_201_CREATED)

    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_product_images(request, product_id):
    """
    Upload images for a product
    POST /api/products/{product_id}/images
    Body (form-data): image files (up to 5)
    """

    if request.user.user_type != 'seller':
        return Response({
            'success': False,
            'message': 'Only sellers can upload images'
        }, status=status.HTTP_403_FORBIDDEN)

    try:
        product = Product.objects.get(id=product_id, shop__owner=request.user)
    except Product.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Product not found or you don\'t have permission'
        }, status=status.HTTP_404_NOT_FOUND)

    # Check existing images count
    existing_count = product.images.count()
    if existing_count >= 5:
        return Response({
            'success': False,
            'message': 'Maximum 5 images allowed per product'
        }, status=status.HTTP_400_BAD_REQUEST)

    uploaded_urls = []

    # Handle multiple file upload
    for key in request.FILES:
        if existing_count + len(uploaded_urls) >= 5:
            break

        image_file = request.FILES[key]

        # Upload to Firebase Storage
        image_path = f"products/{product.id}/{image_file.name}"
        image_url = upload_to_firebase_storage(image_file, image_path)

        if image_url:
            # Create ProductImage record
            ProductImage.objects.create(
                product=product,
                image_url=image_url,
                display_order=existing_count + len(uploaded_urls) + 1
            )
            uploaded_urls.append(image_url)

    return Response({
        'success': True,
        'message': f'{len(uploaded_urls)} image(s) uploaded successfully',
        'images': uploaded_urls
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def list_products(request):
    """
    List all active products with filters
    GET /api/products
    Query params:
    - category (id)
    - shop (id)
    - search (product name)
    - min_price, max_price (based on display_price)
    - sizes, colors (comma-separated)
    - sort (price_low, price_high, newest)
    """

    products = Product.objects.filter(
        is_active=True,
        shop__is_approved=True,
        shop__is_active=True
    ).select_related('shop', 'category').prefetch_related('images')

    # Filters
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)

    shop_id = request.GET.get('shop')
    if shop_id:
        products = products.filter(shop_id=shop_id)

    search = request.GET.get('search')
    if search:
        products = products.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )

    # Price range (based on display_price - what customer pays)
    min_price = request.GET.get('min_price')
    if min_price:
        products = products.filter(display_price__gte=min_price)

    max_price = request.GET.get('max_price')
    if max_price:
        products = products.filter(display_price__lte=max_price)

    # Sizes filter
    sizes = request.GET.get('sizes')
    if sizes:
        size_list = sizes.split(',')
        for size in size_list:
            products = products.filter(sizes__contains=[size.strip()])

    # Colors filter
    colors = request.GET.get('colors')
    if colors:
        color_list = colors.split(',')
        for color in color_list:
            products = products.filter(colors__contains=[color.strip()])

    # Sorting
    sort = request.GET.get('sort', 'newest')
    if sort == 'price_low':
        products = products.order_by('display_price')
    elif sort == 'price_high':
        products = products.order_by('-display_price')
    elif sort == 'popular':
        products = products.order_by('-total_sales')
    else:  # newest
        products = products.order_by('-created_at')

    # Pagination
    paginator = ProductPagination()
    paginated_products = paginator.paginate_queryset(products, request)

    serializer = ProductSerializer(paginated_products, many=True, context={'request': request})

    return paginator.get_paginated_response({
        'success': True,
        'products': serializer.data
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_product_detail(request, product_id):
    """
    Get product details
    GET /api/products/{product_id}
    """
    try:
        product = Product.objects.select_related('shop', 'category').prefetch_related('images').get(
            id=product_id,
            is_active=True
        )

        serializer = ProductDetailSerializer(product, context={'request': request})

        return Response({
            'success': True,
            'product': serializer.data
        }, status=status.HTTP_200_OK)

    except Product.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Product not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_product(request, product_id):
    """
    Update product (Seller only)
    PUT /api/products/{product_id}
    """

    if request.user.user_type != 'seller':
        return Response({
            'success': False,
            'message': 'Only sellers can update products'
        }, status=status.HTTP_403_FORBIDDEN)

    try:
        product = Product.objects.get(id=product_id, shop__owner=request.user)
    except Product.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Product not found or you don\'t have permission'
        }, status=status.HTTP_404_NOT_FOUND)

    serializer = ProductCreateSerializer(product, data=request.data, partial=True, context={'request': request})

    if serializer.is_valid():
        product = serializer.save()

        return Response({
            'success': True,
            'message': 'Product updated successfully',
            'product': ProductSerializer(product, context={'request': request}).data
        }, status=status.HTTP_200_OK)

    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_product(request, product_id):
    """
    Delete product (soft delete)
    DELETE /api/products/{product_id}
    """

    if request.user.user_type != 'seller':
        return Response({
            'success': False,
            'message': 'Only sellers can delete products'
        }, status=status.HTTP_403_FORBIDDEN)

    try:
        product = Product.objects.get(id=product_id, shop__owner=request.user)
        product.is_active = False
        product.save()

        return Response({
            'success': True,
            'message': 'Product deleted successfully'
        }, status=status.HTTP_200_OK)

    except Product.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Product not found or you don\'t have permission'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def list_categories(request):
    """
    Get all categories with subcategories
    GET /api/categories
    """
    # Get only parent categories (no parent)
    categories = Category.objects.filter(
        parent__isnull=True,
        is_active=True
    ).prefetch_related('subcategories')

    serializer = CategorySerializer(categories, many=True)

    return Response({
        'success': True,
        'categories': serializer.data
    }, status=status.HTTP_200_OK)