from rest_framework import serializers
from .models import ProductReview
from apps.orders.models import Order


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating reviews"""

    order_number = serializers.CharField(write_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ProductReview
        fields = ('order_number', 'product_id', 'rating', 'review_text')

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value

    def validate(self, data):
        """Validate order and product"""
        from apps.products.models import Product

        # Get order
        try:
            order = Order.objects.get(order_number=data['order_number'])
        except Order.DoesNotExist:
            raise serializers.ValidationError({'order_number': 'Order not found'})

        # Check if order is delivered
        if order.order_status != 'delivered':
            raise serializers.ValidationError({'order': 'Can only review delivered orders'})

        # Check if user is the customer
        request = self.context['request']
        if order.customer != request.user:
            raise serializers.ValidationError({'order': 'You can only review your own orders'})

        # Get product
        try:
            product = Product.objects.get(id=data['product_id'])
        except Product.DoesNotExist:
            raise serializers.ValidationError({'product_id': 'Product not found'})

        # Check if product is in this order
        if not order.items.filter(product=product).exists():
            raise serializers.ValidationError({'product': 'Product not in this order'})

        # Check if already reviewed
        if ProductReview.objects.filter(order=order, product=product).exists():
            raise serializers.ValidationError({'review': 'You have already reviewed this product'})

        data['order'] = order
        data['product'] = product

        return data

    def create(self, validated_data):
        """Create review and update product rating"""
        order_number = validated_data.pop('order_number')
        product_id = validated_data.pop('product_id')

        order = validated_data['order']
        product = validated_data['product']
        customer = self.context['request'].user

        # Create review
        review = ProductReview.objects.create(
            order=order,
            product=product,
            customer=customer,
            rating=validated_data['rating'],
            review_text=validated_data.get('review_text', '')
        )

        # Update product average rating
        from django.db.models import Avg
        avg_rating = ProductReview.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
        total_reviews = ProductReview.objects.filter(product=product).count()

        product.average_rating = round(avg_rating, 2)
        product.total_reviews = total_reviews
        product.save(update_fields=['average_rating', 'total_reviews'])

        return review


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for displaying reviews"""

    customer_name = serializers.SerializerMethodField()

    class Meta:
        model = ProductReview
        fields = ('id', 'customer_name', 'rating', 'review_text',
                  'is_verified_purchase', 'created_at')

    def get_customer_name(self, obj):
        """Return only first name for privacy"""
        full_name = obj.customer.full_name
        parts = full_name.split()
        if len(parts) > 1:
            return f"{parts[0]} {parts[1][0]}."  # e.g., "John D."
        return parts[0]