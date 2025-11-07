from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('phone_number', 'full_name', 'user_type', 'is_phone_verified', 'created_at')
    list_filter = ('user_type', 'is_phone_verified', 'is_active')
    search_fields = ('phone_number', 'full_name', 'email')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal info', {'fields': ('full_name', 'email', 'user_type', 'firebase_uid')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_phone_verified')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )

    readonly_fields = ('created_at', 'updated_at')
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'full_name', 'user_type', 'password1', 'password2'),
        }),
    )