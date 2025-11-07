from django.db import models
from apps.accounts.models import CustomUser
from apps.products.models import Product
from apps.orders.models import Order
from django.core.validators import MinValueValidator, MaxValueValidator


class ProductReview(models.Model):
    """Product reviews by customers"""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reviews')

    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review_text = models.TextField(max_length=500, blank=True)

    is_verified_purchase = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'product_reviews'
        verbose_name = 'Product Review'
        verbose_name_plural = 'Product Reviews'
        ordering = ['-created_at']
        unique_together = ('order', 'product')  # One review per product per order
        indexes = [
            models.Index(fields=['product', '-created_at']),
        ]

    def __str__(self):
        return f"{self.customer.full_name} - {self.product.name} ({self.rating}★)"