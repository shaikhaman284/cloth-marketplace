from django.contrib import admin
from .models import Shop
from django.utils import timezone


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('shop_name', 'owner', 'city', 'approval_status', 'commission_rate', 'created_at')
    list_filter = ('approval_status', 'is_active', 'city')
    search_fields = ('shop_name', 'owner__phone_number', 'city')
    readonly_fields = ('created_at', 'approved_at')

    fieldsets = (
        ('Shop Information', {
            'fields': ('owner', 'shop_name', 'business_address', 'city', 'pincode',
                       'owner_contact_number', 'gst_number', 'shop_image_url')
        }),
        ('Approval', {
            'fields': ('approval_status', 'is_approved', 'rejection_reason', 'approved_at')
        }),
        ('Settings', {
            'fields': ('commission_rate', 'is_active', 'created_at')
        }),
    )

    actions = ['approve_shops', 'reject_shops']

    def approve_shops(self, request, queryset):
        """Bulk approve shops"""
        updated = queryset.update(
            approval_status='approved',
            is_approved=True,
            approved_at=timezone.now()
        )
        self.message_user(request, f'{updated} shop(s) approved successfully.')

    approve_shops.short_description = "Approve selected shops"

    def reject_shops(self, request, queryset):
        """Bulk reject shops"""
        updated = queryset.update(
            approval_status='rejected',
            is_approved=False
        )
        self.message_user(request, f'{updated} shop(s) rejected.')

    reject_shops.short_description = "Reject selected shops"