from rest_framework import serializers
from .models import Category, Product, ProductImage
from apps.shops.models import Shop
from decimal import Decimal

from rest_framework import serializers
from .models import Category, Product, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'icon_url', 'display_order', 'subcategories')

    def get_subcategories(self, obj):
        if obj.subcategories.exists():
            return CategorySerializer(obj.subcategories.filter(is_active=True), many=True).data
        return []


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'image_url', 'display_order')


class ProductCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating products (seller side)"""

    class Meta:
        model = Product
        fields = ('category', 'name', 'description', 'base_price', 'stock_quantity',
                  'sizes', 'colors', 'material', 'brand')

    def validate_base_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Base price must be greater than 0")
        return value

    def validate_stock_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative")
        return value

    def create(self, validated_data):
        # Get shop from request user
        shop = self.context['request'].user.shop

        # Set shop and commission rate
        validated_data['shop'] = shop
        validated_data['commission_rate'] = shop.commission_rate

        # Product model's save() method will auto-calculate display_price
        product = Product.objects.create(**validated_data)

        return product


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for displaying products"""

    images = ProductImageSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    shop_name = serializers.CharField(source='shop.shop_name', read_only=True)
    shop_city = serializers.CharField(source='shop.city', read_only=True)

    # For sellers: show both prices
    # For customers: only show display_price

    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'base_price', 'commission_rate',
                  'display_price', 'stock_quantity', 'sizes', 'colors', 'material',
                  'brand', 'average_rating', 'total_reviews', 'category_name',
                  'shop_name', 'shop_city', 'images', 'is_active', 'created_at')
        read_only_fields = ('id', 'display_price', 'average_rating', 'total_reviews',
                            'commission_rate', 'created_at')

    def to_representation(self, instance):
        """Customize response based on user type"""
        data = super().to_representation(instance)
        request = self.context.get('request')

        # If customer is viewing, hide base_price and commission_rate
        if request and request.user.is_authenticated:
            if request.user.user_type == 'customer':
                data.pop('base_price', None)
                data.pop('commission_rate', None)
        # If anonymous user (website), also hide
        elif request and not request.user.is_authenticated:
            data.pop('base_price', None)
            data.pop('commission_rate', None)

        return data


class ProductDetailSerializer(ProductSerializer):
    """Detailed product view with related products"""

    shop_details = serializers.SerializerMethodField()

    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ('shop_details',)

    def get_shop_details(self, obj):
        return {
            'id': obj.shop.id,
            'name': obj.shop.shop_name,
            'city': obj.shop.city,
            'address': obj.shop.business_address,
            'image': obj.shop.shop_image_url,
        }