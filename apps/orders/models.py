from django.db import models
from apps.accounts.models import CustomUser
from apps.shops.models import Shop
from apps.products.models import Product
from decimal import Decimal
import random
import string
from django.utils import timezone


def generate_order_number():
    """Generate unique order number: ORD20250115001"""
    date_str = timezone.now().strftime('%Y%m%d')
    random_str = ''.join(random.choices(string.digits, k=3))
    return f"ORD{date_str}{random_str}"


class Order(models.Model):
    """Customer orders with correct commission model"""

    ORDER_STATUS_CHOICES = (
        ('placed', 'Placed'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )

    PAYMENT_STATUS_CHOICES = (
        ('cod_pending', 'COD Pending'),
        ('cod_collected', 'COD Collected'),
        ('online_pending', 'Online Pending'),
        ('online_completed', 'Online Completed'),
        ('refunded', 'Refunded'),
    )

    order_number = models.CharField(max_length=20, unique=True, default=generate_order_number)
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='orders')

    # Delivery details
    delivery_name = models.CharField(max_length=100)
    delivery_phone = models.CharField(max_length=15)
    delivery_address = models.TextField()
    delivery_city = models.CharField(max_length=100)
    delivery_pincode = models.CharField(max_length=6)
    delivery_landmark = models.CharField(max_length=200, blank=True)

    # Pricing breakdown
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)  # Sum of item display_prices
    cod_fee = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)  # subtotal + cod_fee - discount

    # Commission tracking
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Platform earns this
    seller_payout_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Seller receives this

    # Status tracking
    payment_method = models.CharField(max_length=20, default='cod')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='cod_pending')
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='placed')

    # Timestamps
    placed_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(blank=True, null=True)
    shipped_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)
    cancellation_reason = models.TextField(blank=True)

    # Notes
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'orders'
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-placed_at']
        indexes = [
            models.Index(fields=['customer', '-placed_at']),
            models.Index(fields=['shop', '-placed_at']),
            models.Index(fields=['order_status']),
        ]

    def __str__(self):
        return f"{self.order_number} - {self.customer.full_name}"


class OrderItem(models.Model):
    """Individual items in an order with price snapshots"""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)

    # Snapshots (saved at order time, don't change if product changes)
    product_name = models.CharField(max_length=200)
    product_image_url = models.URLField(max_length=500, blank=True)

    # CRITICAL: Price snapshots with correct model
    base_price = models.DecimalField(max_digits=10, decimal_places=2)  # What seller gets per unit
    display_price = models.DecimalField(max_digits=10, decimal_places=2)  # What customer pays per unit
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2)  # % at time of order
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Per unit: display - base

    # Order details
    quantity = models.IntegerField(default=1)
    selected_size = models.CharField(max_length=20, blank=True)
    selected_color = models.CharField(max_length=50, blank=True)

    # Calculated totals
    item_subtotal = models.DecimalField(max_digits=10, decimal_places=2)  # display_price × quantity (customer pays)
    seller_amount = models.DecimalField(max_digits=10, decimal_places=2)  # base_price × quantity (seller gets)

    class Meta:
        db_table = 'order_items'
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def save(self, *args, **kwargs):
        """Auto-calculate amounts"""
        self.commission_amount = self.display_price - self.base_price
        self.item_subtotal = self.display_price * Decimal(str(self.quantity))
        self.seller_amount = self.base_price * Decimal(str(self.quantity))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"