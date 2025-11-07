from django.db import models
from apps.accounts.models import CustomUser


class Shop(models.Model):
    """Seller's shop information"""

    APPROVAL_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    owner = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='shop')
    shop_name = models.CharField(max_length=200)
    business_address = models.TextField()
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=6)
    owner_contact_number = models.CharField(max_length=15)
    gst_number = models.CharField(max_length=15, blank=True, null=True)
    shop_image_url = models.URLField(max_length=500, blank=True, null=True)

    # Approval workflow
    is_approved = models.BooleanField(default=False)
    approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True, null=True)

    # Commission settings
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=15.00)  # 15%

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'shops'
        verbose_name = 'Shop'
        verbose_name_plural = 'Shops'

    def __str__(self):
        return self.shop_name