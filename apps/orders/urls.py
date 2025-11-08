from django.urls import path
from . import views

urlpatterns = [
    path('create', views.create_order, name='create-order'),
    path('my-orders', views.my_orders, name='my-orders'),
    path('statistics', views.order_statistics, name='order-statistics'),  # Add before detail route
    path('<str:order_number>', views.get_order_detail, name='order-detail'),
    path('<str:order_number>/status', views.update_order_status, name='update-order-status'),  # Add
    path('<str:order_number>/cancel', views.cancel_order, name='cancel-order'),  # Add
]