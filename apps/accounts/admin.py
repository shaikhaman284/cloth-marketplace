from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('phone_number', 'full_name', 'user_type', 'is_phone_verified', 'is_staff', 'created_at')
    list_filter = ('user_type', 'is_phone_verified', 'is_active', 'is_staff')
    search_fields = ('phone_number', 'full_name', 'email')
    ordering = ('-created_at',)

    # CRITICAL: Fix fieldsets for phone-based login
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal info', {'fields': ('full_name', 'email', 'user_type', 'firebase_uid')}),
        ('Permissions',
         {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_phone_verified', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )

    readonly_fields = ('created_at', 'updated_at', 'last_login')

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'full_name', 'user_type', 'password1', 'password2', 'is_staff', 'is_superuser'),
        }),
    )

    # CRITICAL: Override get_fieldsets to remove username requirement
    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)