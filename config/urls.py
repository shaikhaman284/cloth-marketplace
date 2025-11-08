"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.core.admin import custom_admin_site  # Import custom admin

# Register all models with custom admin site
from django.apps import apps

# Auto-register all models
for model in apps.get_models():
    try:
        custom_admin_site.register(model)
    except admin.sites.AlreadyRegistered:
        pass

# Import and register with customizations
from apps.accounts.admin import CustomUserAdmin
from apps.shops.admin import ShopAdmin
from apps.products.admin import CategoryAdmin, ProductAdmin
from apps.orders.admin import OrderAdmin
from apps.reviews.admin import ProductReviewAdmin

from apps.accounts.models import CustomUser
from apps.shops.models import Shop
from apps.products.models import Category, Product
from apps.orders.models import Order
from apps.reviews.models import ProductReview

# Unregister and re-register with customizations
custom_admin_site._registry = {}  # Clear registry
custom_admin_site.register(CustomUser, CustomUserAdmin)
custom_admin_site.register(Shop, ShopAdmin)
custom_admin_site.register(Category, CategoryAdmin)
custom_admin_site.register(Product, ProductAdmin)
custom_admin_site.register(Order, OrderAdmin)
custom_admin_site.register(ProductReview, ProductReviewAdmin)

urlpatterns = [
    path('admin/', custom_admin_site.urls),  # Use custom admin
    path('api/auth/', include('apps.accounts.urls')),
    path('api/shops/', include('apps.shops.urls')),
    path('api/', include('apps.products.urls')),
    path('api/orders/', include('apps.orders.urls')),
    path('api/reviews/', include('apps.reviews.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)