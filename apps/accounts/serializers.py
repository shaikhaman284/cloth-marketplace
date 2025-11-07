from rest_framework import serializers
from .models import CustomUser
from config.firebase_config import verify_firebase_token


class UserRegistrationSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    full_name = serializers.CharField(max_length=100)
    user_type = serializers.ChoiceField(choices=['seller', 'customer'])
    firebase_id_token = serializers.CharField(write_only=True)

    def validate_firebase_id_token(self, value):
        """Verify Firebase token"""
        decoded_token = verify_firebase_token(value)
        if not decoded_token:
            raise serializers.ValidationError("Invalid Firebase token")
        return decoded_token

    def create(self, validated_data):
        decoded_token = validated_data.pop('firebase_id_token')
        firebase_uid = decoded_token['uid']

        # Get or create user
        user, created = CustomUser.objects.get_or_create(
            phone_number=validated_data['phone_number'],
            defaults={
                'full_name': validated_data['full_name'],
                'user_type': validated_data['user_type'],
                'firebase_uid': firebase_uid,
                'is_phone_verified': True,
            }
        )

        return user


class UserSerializer(serializers.ModelSerializer):
    has_shop = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('id', 'phone_number', 'full_name', 'email', 'user_type',
                  'is_phone_verified', 'has_shop', 'created_at')
        read_only_fields = ('id', 'created_at')

    def get_has_shop(self, obj):
        """Check if seller has registered shop"""
        if obj.user_type == 'seller':
            return hasattr(obj, 'shop')
        return None