from rest_framework import serializers
from .models import Order, OrderItem
from apps.products.serializers import ProductSerializer
from .utils import OrderCalculator


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order items"""

    product_info = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ('id', 'product_name', 'product_image_url', 'base_price',
                  'display_price', 'commission_rate', 'commission_amount',
                  'quantity', 'selected_size', 'selected_color',
                  'item_subtotal', 'seller_amount', 'product_info')

    def get_product_info(self, obj):
        """Include basic product info"""
        if obj.product:
            return {
                'id': obj.product.id,
                'name': obj.product.name,
                'is_active': obj.product.is_active
            }
        return None


class OrderCreateSerializer(serializers.Serializer):
    """Serializer for creating orders"""

    cart_items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )

    # Delivery details
    delivery_name = serializers.CharField(max_length=100)
    delivery_phone = serializers.CharField(max_length=15)
    delivery_address = serializers.CharField()
    delivery_city = serializers.CharField(max_length=100)
    delivery_pincode = serializers.CharField(max_length=6)
    delivery_landmark = serializers.CharField(max_length=200, required=False, allow_blank=True)

    def validate(self, data):
        """Validate cart and delivery address"""

        # Validate delivery address
        delivery_data = {
            'name': data.get('delivery_name'),
            'phone': data.get('delivery_phone'),
            'address': data.get('delivery_address'),
            'city': data.get('delivery_city'),
            'pincode': data.get('delivery_pincode')
        }

        is_valid, errors = OrderCalculator.validate_delivery_address(delivery_data)
        if not is_valid:
            raise serializers.ValidationError({'delivery': errors})

        # Validate cart items
        cart_items = data.get('cart_items', [])
        is_valid, errors, validated_items = OrderCalculator.validate_cart_items(cart_items)

        if not is_valid:
            raise serializers.ValidationError({'cart_items': errors})

        # Store validated items for create method
        data['_validated_items'] = validated_items

        return data

    def create(self, validated_data):
        """Create order with correct pricing"""
        from django.db import transaction

        # Get validated items
        validated_items = validated_data.pop('_validated_items')

        # Calculate order totals
        calc_data = OrderCalculator.calculate_order_totals(validated_items)

        # Get customer from request
        customer = self.context['request'].user

        with transaction.atomic():
            # Create Order
            order = Order.objects.create(
                customer=customer,
                shop=calc_data['shop'],

                # Delivery details
                delivery_name=validated_data['delivery_name'],
                delivery_phone=validated_data['delivery_phone'],
                delivery_address=validated_data['delivery_address'],
                delivery_city=validated_data['delivery_city'].title(),
                delivery_pincode=validated_data['delivery_pincode'],
                delivery_landmark=validated_data.get('delivery_landmark', ''),

                # Pricing (correct model)
                subtotal=calc_data['subtotal'],
                cod_fee=calc_data['cod_fee'],
                total_amount=calc_data['total_amount'],
                commission_amount=calc_data['total_commission'],
                seller_payout_amount=calc_data['seller_payout_amount'],

                # Status
                payment_method='cod',
                payment_status='cod_pending',
                order_status='placed'
            )

            # Create OrderItems with price snapshots
            for item_data in calc_data['items_breakdown']:
                product = item_data['product']

                # Get first product image
                first_image = product.images.first()
                image_url = first_image.image_url if first_image else ''

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    product_image_url=image_url,

                    # Price snapshots (CRITICAL)
                    base_price=item_data['base_price'],
                    display_price=item_data['display_price'],
                    commission_rate=item_data['commission_rate'],
                    commission_amount=item_data['commission_per_unit'],

                    # Order details
                    quantity=item_data['quantity'],
                    selected_size=item_data['size'],
                    selected_color=item_data['color'],

                    # Calculated amounts
                    item_subtotal=item_data['item_subtotal'],
                    seller_amount=item_data['item_seller_amount']
                )

                # Reduce product stock
                product.stock_quantity -= item_data['quantity']
                product.save(update_fields=['stock_quantity'])

            return order


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for displaying orders"""

    items = OrderItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    customer_phone = serializers.CharField(source='customer.phone_number', read_only=True)
    shop_name = serializers.CharField(source='shop.shop_name', read_only=True)
    shop_city = serializers.CharField(source='shop.city', read_only=True)
    items_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ('id', 'order_number', 'customer_name', 'customer_phone',
                  'shop_name', 'shop_city', 'delivery_name', 'delivery_phone',
                  'delivery_address', 'delivery_city', 'delivery_pincode',
                  'delivery_landmark', 'subtotal', 'cod_fee', 'discount_amount',
                  'total_amount', 'commission_amount', 'seller_payout_amount',
                  'payment_method', 'payment_status', 'order_status',
                  'placed_at', 'confirmed_at', 'shipped_at', 'delivered_at',
                  'cancelled_at', 'cancellation_reason', 'items', 'items_count')
        read_only_fields = ('id', 'order_number', 'placed_at')

    def get_items_count(self, obj):
        return obj.items.count()

    def to_representation(self, instance):
        """Customize response based on user type"""
        data = super().to_representation(instance)
        request = self.context.get('request')

        if request and request.user.is_authenticated:
            # If customer viewing, hide some seller details
            if request.user.user_type == 'customer':
                data.pop('commission_amount', None)
                data.pop('seller_payout_amount', None)
                # Hide base prices in items
                if 'items' in data:
                    for item in data['items']:
                        item.pop('base_price', None)
                        item.pop('commission_rate', None)
                        item.pop('commission_amount', None)
                        item.pop('seller_amount', None)

        return data