from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import ProductReview
from .serializers import ReviewCreateSerializer, ReviewSerializer


class ReviewPagination(PageNumberPagination):
    page_size = 10


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_review(request):
    """
    Create product review
    POST /api/reviews/create

    Body:
    {
        "order_number": "ORD20250116001",
        "product_id": 1,
        "rating": 5,
        "review_text": "Great product!"
    }
    """

    if request.user.user_type != 'customer':
        return Response({
            'success': False,
            'message': 'Only customers can write reviews'
        }, status=status.HTTP_403_FORBIDDEN)

    serializer = ReviewCreateSerializer(data=request.data, context={'request': request})

    if serializer.is_valid():
        review = serializer.save()
        review_serializer = ReviewSerializer(review)

        return Response({
            'success': True,
            'message': 'Review submitted successfully',
            'review': review_serializer.data
        }, status=status.HTTP_201_CREATED)

    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def list_product_reviews(request, product_id):
    """
    List reviews for a product
    GET /api/products/{product_id}/reviews?sort=newest

    Sort options: newest, highest, lowest
    """

    reviews = ProductReview.objects.filter(product_id=product_id).select_related('customer')

    # Sorting
    sort = request.GET.get('sort', 'newest')
    if sort == 'highest':
        reviews = reviews.order_by('-rating', '-created_at')
    elif sort == 'lowest':
        reviews = reviews.order_by('rating', '-created_at')
    else:  # newest
        reviews = reviews.order_by('-created_at')

    # Pagination
    paginator = ReviewPagination()
    paginated_reviews = paginator.paginate_queryset(reviews, request)

    serializer = ReviewSerializer(paginated_reviews, many=True)

    return paginator.get_paginated_response({
        'success': True,
        'reviews': serializer.data
    })