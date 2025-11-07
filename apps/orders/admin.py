from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('product_name', 'base_price', 'display_price', 'commission_amount',
                       'quantity', 'item_subtotal', 'seller_amount')
    extra = 0
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer', 'shop', 'total_amount', 'seller_payout_amount',
                    'commission_amount', 'order_status', 'payment_status', 'placed_at')
    list_filter = ('order_status', 'payment_status', 'payment_method', 'placed_at')
    search_fields = ('order_number', 'customer__phone_number', 'shop__shop_name')
    readonly_fields = ('order_number', 'subtotal', 'total_amount', 'commission_amount',
                       'seller_payout_amount', 'placed_at', 'confirmed_at', 'shipped_at',
                       'delivered_at', 'cancelled_at')
    inlines = [OrderItemInline]

    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'customer', 'shop', 'placed_at')
        }),
        ('Delivery Details', {
            'fields': ('delivery_name', 'delivery_phone', 'delivery_address', 'delivery_city',
                       'delivery_pincode', 'delivery_landmark')
        }),
        ('Pricing Breakdown', {
            'fields': ('subtotal', 'cod_fee', 'discount_amount', 'total_amount',
                       'commission_amount', 'seller_payout_amount'),
            'description': 'Total = what customer pays. Seller payout = what seller receives. Commission = platform earns.'
        }),
        ('Status', {
            'fields': ('order_status', 'payment_method', 'payment_status')
        }),
        ('Timestamps', {
            'fields': ('confirmed_at', 'shipped_at', 'delivered_at', 'cancelled_at', 'cancellation_reason')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )