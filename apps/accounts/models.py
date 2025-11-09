from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import uuid  # ← ADD THIS IMPORT


class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, full_name, user_type, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Users must have a phone number")

        # ↓ ADD THESE 4 LINES ↓
        # Handle firebase_uid - generate if not provided
        firebase_uid = extra_fields.pop('firebase_uid', None)
        if not firebase_uid:
            firebase_uid = f'admin_{uuid.uuid4().hex[:20]}'

        user = self.model(
            phone_number=phone_number,
            full_name=full_name,
            user_type=user_type,
            firebase_uid=firebase_uid,  # ← ADD THIS LINE
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, full_name, user_type='seller', password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is False:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is False:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(
            phone_number=phone_number,
            full_name=full_name,
            user_type=user_type,
            password=password,
            **extra_fields
        )


# ← CustomUser class stays EXACTLY the same, no changes needed
class CustomUser(AbstractUser):
    USER_TYPES = (
        ('seller', 'Seller'),
        ('customer', 'Customer'),
    )

    username = None  # remove username
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(blank=True, null=True)
    full_name = models.CharField(max_length=100)
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    firebase_uid = models.CharField(max_length=128, unique=True)
    fcm_token = models.CharField(max_length=255, blank=True, null=True)

    is_phone_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['full_name', 'user_type']

    objects = CustomUserManager()

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.full_name} ({self.phone_number})"