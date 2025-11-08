from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta
from apps.orders.models import Order
from apps.shops.models import Shop
from apps.products.models import Product
from apps.accounts.models import CustomUser


class CustomAdminSite(admin.AdminSite):
    site_header = 'ClothMarket Admin'
    site_title = 'ClothMarket Admin Portal'
    index_title = 'Platform Management'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.custom_dashboard), name='custom_dashboard'),
        ]
        return custom_urls + urls

    def index(self, request, extra_context=None):
        """Override default admin index to show custom dashboard"""
        return self.custom_dashboard(request)

    def custom_dashboard(self, request):
        """Custom dashboard with revenue metrics"""

        # Date ranges
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        # User statistics
        total_users = CustomUser.objects.count()
        total_sellers = CustomUser.objects.filter(user_type='seller').count()
        total_customers = CustomUser.objects.filter(user_type='customer').count()

        # Shop statistics
        total_shops = Shop.objects.count()
        approved_shops = Shop.objects.filter(is_approved=True).count()
        pending_shops = Shop.objects.filter(approval_status='pending').count()

        # Product statistics
        total_products = Product.objects.count()
        active_products = Product.objects.filter(is_active=True).count()

        # Order statistics
        all_orders = Order.objects.all()
        total_orders = all_orders.count()

        # Revenue calculations
        delivered_orders = all_orders.filter(order_status='delivered')

        total_gmv = delivered_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        total_commission = delivered_orders.aggregate(Sum('commission_amount'))['commission_amount__sum'] or 0
        total_seller_payouts = delivered_orders.aggregate(Sum('seller_payout_amount'))['seller_payout_amount__sum'] or 0
        total_cod_fees = delivered_orders.count() * 50  # ₹50 per COD order

        # Today's metrics
        today_orders = all_orders.filter(placed_at__date=today)
        today_delivered = today_orders.filter(order_status='delivered')
        today_revenue = today_delivered.aggregate(Sum('commission_amount'))['commission_amount__sum'] or 0

        # This week
        week_orders = all_orders.filter(placed_at__date__gte=week_ago)
        week_delivered = week_orders.filter(order_status='delivered')
        week_revenue = week_delivered.aggregate(Sum('commission_amount'))['commission_amount__sum'] or 0

        # This month
        month_orders = all_orders.filter(placed_at__date__gte=month_ago)
        month_delivered = month_orders.filter(order_status='delivered')
        month_revenue = month_delivered.aggregate(Sum('commission_amount'))['commission_amount__sum'] or 0

        # Order status breakdown
        order_status_counts = {
            'placed': all_orders.filter(order_status='placed').count(),
            'confirmed': all_orders.filter(order_status='confirmed').count(),
            'shipped': all_orders.filter(order_status='shipped').count(),
            'delivered': all_orders.filter(order_status='delivered').count(),
            'cancelled': all_orders.filter(order_status='cancelled').count(),
        }

        # Recent orders
        recent_orders = all_orders.select_related('customer', 'shop').order_by('-placed_at')[:10]

        # Top performing shops
        top_shops = Shop.objects.filter(
            is_approved=True
        ).annotate(
            total_orders=Count('orders'),
            total_revenue=Sum('orders__seller_payout_amount', filter=Count('orders__order_status' == 'delivered'))
        ).order_by('-total_orders')[:5]

        context = {
            **self.each_context(request),
            'title': 'Dashboard',

            # User stats
            'total_users': total_users,
            'total_sellers': total_sellers,
            'total_customers': total_customers,

            # Shop stats
            'total_shops': total_shops,
            'approved_shops': approved_shops,
            'pending_shops': pending_shops,

            # Product stats
            'total_products': total_products,
            'active_products': active_products,

            # Order stats
            'total_orders': total_orders,
            'order_status_counts': order_status_counts,

            # Revenue stats
            'total_gmv': round(total_gmv, 2),
            'total_commission': round(total_commission, 2),
            'total_seller_payouts': round(total_seller_payouts, 2),
            'total_cod_fees': round(total_cod_fees, 2),
            'platform_revenue': round(total_commission + total_cod_fees, 2),

            # Time-based revenue
            'today_orders': today_orders.count(),
            'today_revenue': round(today_revenue, 2),
            'week_orders': week_orders.count(),
            'week_revenue': round(week_revenue, 2),
            'month_orders': month_orders.count(),
            'month_revenue': round(month_revenue, 2),

            # Recent data
            'recent_orders': recent_orders,
            'top_shops': top_shops,
        }

        return render(request, 'admin/custom_dashboard.html', context)


# Create custom admin site instance
custom_admin_site = CustomAdminSite(name='custom_admin')