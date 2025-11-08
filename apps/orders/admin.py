from django.contrib import admin
from .models import Order, OrderItem
from django.utils.html import format_html
from django.db.models import Sum


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('product_name', 'product_image_preview', 'base_price', 'display_price',
                       'commission_rate', 'commission_amount', 'quantity', 'selected_size',
                       'selected_color', 'item_subtotal', 'seller_amount')
    extra = 0
    can_delete = False

    def product_image_preview(self, obj):
        if obj.product_image_url:
            return format_html('<img src="{}" width="50" height="50" />', obj.product_image_url)
        return '-'

    product_image_preview.short_description = 'Image'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer_link', 'shop_link', 'total_amount_display',
                    'seller_payout_display', 'commission_display', 'order_status_badge',
                    'payment_status', 'placed_at')
    list_filter = ('order_status', 'payment_status', 'payment_method', 'placed_at', 'shop')
    search_fields = ('order_number', 'customer__phone_number', 'customer__full_name',
                     'shop__shop_name', 'delivery_phone')
    readonly_fields = ('order_number', 'pricing_breakdown', 'status_timeline', 'subtotal',
                       'total_amount', 'commission_amount', 'seller_payout_amount',
                       'placed_at', 'confirmed_at', 'shipped_at', 'delivered_at', 'cancelled_at')
    inlines = [OrderItemInline]
    date_hierarchy = 'placed_at'

    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'customer', 'shop', 'placed_at')
        }),
        ('Delivery Details', {
            'fields': ('delivery_name', 'delivery_phone', 'delivery_address',
                       'delivery_city', 'delivery_pincode', 'delivery_landmark')
        }),
        ('Pricing Breakdown', {
            'fields': ('pricing_breakdown', 'subtotal', 'cod_fee', 'discount_amount',
                       'total_amount', 'commission_amount', 'seller_payout_amount'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('order_status', 'payment_method', 'payment_status', 'status_timeline')
        }),
        ('Timestamps', {
            'fields': ('confirmed_at', 'shipped_at', 'delivered_at', 'cancelled_at', 'cancellation_reason'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )

    def customer_link(self, obj):
        return format_html('<a href="/admin/accounts/customuser/{}/change/">{}</a>',
                           obj.customer.id, obj.customer.full_name)

    customer_link.short_description = 'Customer'

    def shop_link(self, obj):
        return format_html('<a href="/admin/shops/shop/{}/change/">{}</a>',
                           obj.shop.id, obj.shop.shop_name)

    shop_link.short_description = 'Shop'

    def total_amount_display(self, obj):
        return format_html('<strong>₹{}</strong>', obj.total_amount)

    total_amount_display.short_description = 'Total (Customer Pays)'

    def seller_payout_display(self, obj):
        return format_html('<span style="color: green;">₹{}</span>', obj.seller_payout_amount)

    seller_payout_display.short_description = 'Seller Gets'

    def commission_display(self, obj):
        return format_html('<span style="color: blue;">₹{}</span>', obj.commission_amount)

    commission_display.short_description = 'Platform Earns'

    def order_status_badge(self, obj):
        colors = {
            'placed': 'orange',
            'confirmed': 'blue',
            'shipped': 'purple',
            'delivered': 'green',
            'cancelled': 'red'
        }
        color = colors.get(obj.order_status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_order_status_display()
        )

    order_status_badge.short_description = 'Status'

    def pricing_breakdown(self, obj):
        """Show detailed pricing breakdown"""
        html = f"""
        <table style="width: 100%; border-collapse: collapse;">
            <tr style="background: #f8f9fa;">
                <th style="padding: 8px; text-align: left; border: 1px solid #dee2e6;">Description</th>
                <th style="padding: 8px; text-align: right; border: 1px solid #dee2e6;">Amount</th>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #dee2e6;">Items Subtotal</td>
                <td style="padding: 8px; text-align: right; border: 1px solid #dee2e6;">₹{obj.subtotal}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #dee2e6;">COD Fee</td>
                <td style="padding: 8px; text-align: right; border: 1px solid #dee2e6;">₹{obj.cod_fee}</td>
            </tr>
            <tr style="background: #fff3cd;">
                <td style="padding: 8px; border: 1px solid #dee2e6;"><strong>Total (Customer Pays)</strong></td>
                <td style="padding: 8px; text-align: right; border: 1px solid #dee2e6;"><strong>₹{obj.total_amount}</strong></td>
            </tr>
            <tr style="background: #d4edda;">
                <td style="padding: 8px; border: 1px solid #dee2e6;">Seller Receives (Base Prices)</td>
                <td style="padding: 8px; text-align: right; border: 1px solid #dee2e6;">₹{obj.seller_payout_amount}</td>
            </tr>
            <tr style="background: #d1ecf1;">
                <td style="padding: 8px; border: 1px solid #dee2e6;">Platform Commission</td>
                <td style="padding: 8px; text-align: right; border: 1px solid #dee2e6;">₹{obj.commission_amount}</td>
            </tr>
        </table>
        <p style="margin-top: 10px; color: #6c757d;">
            <small>✓ Subtotal = Seller Amount + Commission (₹{obj.subtotal} = ₹{obj.seller_payout_amount} + ₹{obj.commission_amount})</small>
        </p>
        """
        return format_html(html)

    pricing_breakdown.short_description = 'Pricing Details'

    def status_timeline(self, obj):
        """Show order status timeline"""
        statuses = []

        if obj.placed_at:
            statuses.append(f"✓ Placed: {obj.placed_at.strftime('%d %b %Y, %I:%M %p')}")
        if obj.confirmed_at:
            statuses.append(f"✓ Confirmed: {obj.confirmed_at.strftime('%d %b %Y, %I:%M %p')}")
        if obj.shipped_at:
            statuses.append(f"✓ Shipped: {obj.shipped_at.strftime('%d %b %Y, %I:%M %p')}")
        if obj.delivered_at:
            statuses.append(f"✓ Delivered: {obj.delivered_at.strftime('%d %b %Y, %I:%M %p')}")
        if obj.cancelled_at:
            statuses.append(f"✗ Cancelled: {obj.cancelled_at.strftime('%d %b %Y, %I:%M %p')}")

        html = '<ul style="margin: 0; padding-left: 20px;">'
        for status in statuses:
            html += f'<li>{status}</li>'
        html += '</ul>'

        return format_html(html)

    status_timeline.short_description = 'Timeline'