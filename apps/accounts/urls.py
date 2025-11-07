from django.urls import path
from . import views

urlpatterns = [
    path('register', views.register_user, name='register'),
    path('verify-token', views.verify_token, name='verify-token'),
]