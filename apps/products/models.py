from django.db import models
from apps.shops.models import Shop
from decimal import Decimal


class Category(models.Model):
    """Product categories"""

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='subcategories')
    icon_url = models.URLField(max_length=500, blank=True, null=True)
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


class Product(models.Model):
    """Product catalog with correct pricing model"""

    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # CRITICAL: Correct pricing model
    base_price = models.DecimalField(max_digits=10, decimal_places=2)  # What seller receives
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2)  # Copied from shop
    display_price = models.DecimalField(max_digits=10, decimal_places=2)  # What customer pays

    stock_quantity = models.IntegerField(default=0)

    # Variants
    sizes = models.JSONField(default=list, blank=True)  # ["S", "M", "L", "XL"]
    colors = models.JSONField(default=list, blank=True)  # ["Red", "Blue", "Green"]

    # Additional info
    material = models.CharField(max_length=100, blank=True)
    brand = models.CharField(max_length=100, blank=True)

    # Reviews aggregation
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.IntegerField(default=0)
    total_sales = models.IntegerField(default=0)  # For analytics

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['shop', 'is_active']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['-created_at']),
        ]

    def save(self, *args, **kwargs):
        """Auto-calculate display_price before saving"""
        if self.base_price and self.commission_rate:
            # display_price = base_price × (1 + commission_rate/100)
            multiplier = Decimal('1') + (self.commission_rate / Decimal('100'))
            self.display_price = self.base_price * multiplier
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    """Product images"""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField(max_length=500)
    display_order = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'product_images'
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'
        ordering = ['display_order']

    def __str__(self):
        return f"Image for {self.product.name}"