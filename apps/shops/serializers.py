from rest_framework import serializers
from .models import Shop
from config.constants import is_city_serviceable


class ShopRegistrationSerializer(serializers.ModelSerializer):
    shop_image = serializers.ImageField(required=False, write_only=True)

    class Meta:
        model = Shop
        fields = ('shop_name', 'business_address', 'city', 'pincode',
                  'owner_contact_number', 'gst_number', 'shop_image')

    def validate_city(self, value):
        """Validate that city is Amravati"""
        if not is_city_serviceable(value):
            raise serializers.ValidationError(
                "Sorry! We currently deliver only in Amravati city. "
                "We'll expand to your area soon!"
            )
        return value.strip().title()  # Capitalize properly: "Amravati"

    def validate_pincode(self, value):
        """Validate pincode format"""
        if not value.isdigit() or len(value) != 6:
            raise serializers.ValidationError("Pincode must be 6 digits")
        return value


class ShopSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.full_name', read_only=True)
    owner_phone = serializers.CharField(source='owner.phone_number', read_only=True)
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Shop
        fields = ('id', 'shop_name', 'business_address', 'city', 'pincode',
                  'owner_contact_number', 'gst_number', 'shop_image_url',
                  'owner_name', 'owner_phone', 'commission_rate',
                  'is_approved', 'approval_status', 'product_count', 'created_at')
        read_only_fields = ('id', 'is_approved', 'approval_status', 'commission_rate', 'created_at')

    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()