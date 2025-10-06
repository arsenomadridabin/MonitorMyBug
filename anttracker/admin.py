from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Farmer, Device, SensorData, AlertLog


class FarmerInline(admin.StackedInline):
    """Inline admin for Farmer model"""
    model = Farmer
    can_delete = False
    verbose_name_plural = 'Farmer Profile'


class ExtendedUserAdmin(UserAdmin):
    """Extended User admin to include Farmer profile"""
    inlines = (FarmerInline,)


class DeviceAdmin(admin.ModelAdmin):
    """Admin configuration for Device model"""
    list_display = ['device_name', 'device_id', 'farmer', 'location', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'farmer']
    search_fields = ['device_name', 'device_id', 'location']
    readonly_fields = ['api_key', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('device_name', 'device_id', 'farmer', 'location')
        }),
        ('Status & Security', {
            'fields': ('is_active', 'api_key')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class SensorDataAdmin(admin.ModelAdmin):
    """Admin configuration for SensorData model"""
    list_display = ['device', 'timestamp', 'temperature', 'humidity', 'ant_count', 'mealy_bugs_count']
    list_filter = ['timestamp', 'device__farmer', 'is_rainfall', 'is_irrigation']
    search_fields = ['device__device_name', 'device__device_id']
    readonly_fields = ['created_at']
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Device Information', {
            'fields': ('device', 'timestamp')
        }),
        ('Environmental Data', {
            'fields': ('temperature', 'humidity')
        }),
        ('Pest Counts', {
            'fields': ('ant_count', 'mealy_bugs_count')
        }),
        ('Status Flags', {
            'fields': ('is_rainfall', 'is_irrigation')
        }),
        ('System', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


class AlertLogAdmin(admin.ModelAdmin):
    """Admin configuration for AlertLog model"""
    list_display = ['sensor_data', 'alert_type', 'sent_to', 'sent_at']
    list_filter = ['alert_type', 'sent_at', 'sensor_data__device__farmer']
    search_fields = ['sensor_data__device__device_name', 'sent_to']
    readonly_fields = ['sent_at']
    date_hierarchy = 'sent_at'


class FarmerAdmin(admin.ModelAdmin):
    """Admin configuration for Farmer model"""
    list_display = ['user', 'farm_name', 'farm_location', 'ant_threshold_limit', 'created_at']
    list_filter = ['created_at', 'ant_threshold_limit']
    search_fields = ['user__username', 'user__email', 'farm_name', 'farm_location']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Farm Details', {
            'fields': ('farm_name', 'farm_location', 'phone_number')
        }),
        ('Alert Settings', {
            'fields': ('ant_threshold_limit',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# Unregister the default User admin and register our extended version
admin.site.unregister(User)
admin.site.register(User, ExtendedUserAdmin)

# Register our models
admin.site.register(Farmer, FarmerAdmin)
admin.site.register(Device, DeviceAdmin)
admin.site.register(SensorData, SensorDataAdmin)
admin.site.register(AlertLog, AlertLogAdmin)

# Customize admin site header
admin.site.site_header = "MonitorMyBug Administration"
admin.site.site_title = "MonitorMyBug Admin"
admin.site.index_title = "Welcome to MonitorMyBug Administration"
