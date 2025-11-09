from django.contrib import admin

class CustomAdminSite(admin.AdminSite):
    site_header = 'ClothMarket Admin Panel'
    site_title = 'ClothMarket Admin'
    index_title = 'Platform Management'

custom_admin_site = CustomAdminSite(name='custom_admin')