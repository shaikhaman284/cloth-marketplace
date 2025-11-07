from django.urls import path
from . import views

urlpatterns = [
    path('register', views.register_shop, name='register-shop'),
    path('me', views.get_my_shop, name='my-shop'),
    path('approved', views.list_approved_shops, name='approved-shops'),
]