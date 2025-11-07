from django.contrib import admin
from .models import Category, Product, ProductImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'display_order', 'is_active')
    list_filter = ('is_active', 'parent')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'shop', 'category', 'base_price', 'display_price', 'commission_rate',
                    'stock_quantity', 'is_active', 'created_at')
    list_filter = ('is_active', 'category', 'shop')
    search_fields = ('name', 'shop__shop_name')
    readonly_fields = ('display_price', 'average_rating', 'total_reviews', 'total_sales',
                       'created_at', 'updated_at')
    inlines = [ProductImageInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('shop', 'category', 'name', 'description')
        }),
        ('Pricing (Commission Model)', {
            'fields': ('base_price', 'commission_rate', 'display_price'),
            'description': 'Base price is what seller receives. Display price is auto-calculated: base_price × (1 + commission_rate/100)'
        }),
        ('Inventory', {
            'fields': ('stock_quantity', 'sizes', 'colors', 'material', 'brand')
        }),
        ('Statistics', {
            'fields': ('average_rating', 'total_reviews', 'total_sales')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )