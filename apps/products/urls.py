from django.urls import path
from . import views

urlpatterns = [
    path('categories', views.list_categories, name='categories'),
    path('products', views.list_products, name='list-products'),
    path('products/create', views.create_product, name='create-product'),
    path('products/<int:product_id>', views.get_product_detail, name='product-detail'),
    path('products/<int:product_id>/update', views.update_product, name='update-product'),
    path('products/<int:product_id>/delete', views.delete_product, name='delete-product'),
    path('products/<int:product_id>/images', views.upload_product_images, name='upload-product-images'),
]