from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin configuration for CustomUser"""
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'is_active', 'is_staff', 'date_joined'
    )
    list_filter = (
        'is_active', 'is_staff', 'is_superuser', 
        'date_joined', 'last_login'
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('bio', 'avatar')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('email', 'first_name', 'last_name', 'bio')
        }),
    )
