from django.contrib import admin
from django.utils.html import format_html
from .models import AdminUser, AdminLog, PlatformStatistics, SystemConfiguration


@admin.register(AdminUser)
class AdminUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('User Info', {'fields': ('user',)}),
        ('Role & Permissions', {
            'fields': (
                'role',
                'can_suspend_users',
                'can_approve_withdrawals',
                'can_verify_kyc',
                'can_manage_admins'
            )
        }),
        ('Status', {'fields': ('is_active',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(AdminLog)
class AdminLogAdmin(admin.ModelAdmin):
    list_display = ['admin_user', 'action_type', 'resource_type', 'timestamp']
    list_filter = ['action_type', 'resource_type', 'timestamp']
    search_fields = ['admin_user__user__username', 'resource_id']
    readonly_fields = ['created_at']
    fieldsets = (
        ('Admin Info', {'fields': ('admin_user', 'ip_address')}),
        ('Action', {'fields': ('action_type', 'resource_type', 'resource_id')}),
        ('Changes', {'fields': ('old_values', 'new_values')}),
        ('Timestamp', {'fields': ('timestamp',)}),
    )


@admin.register(PlatformStatistics)
class PlatformStatisticsAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_users', 'total_deposits', 'total_withdrawals']
    list_filter = ['date']
    readonly_fields = ['created_at']
    fieldsets = (
        ('Date', {'fields': ('date',)}),
        ('Users', {'fields': ('total_users', 'new_users_today', 'active_users')}),
        ('Funds', {
            'fields': (
                'total_deposits',
                'total_withdrawals',
                'pending_withdrawals',
                'total_aum'
            )
        }),
        ('Platform', {
            'fields': (
                'total_investments',
                'active_investments',
                'total_platform_profit',
                'total_platform_fees'
            )
        }),
        ('KYC', {'fields': ('pending_kyc_count', 'verified_kyc_count')}),
        ('Timestamp', {'fields': ('created_at',)}),
    )


@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    list_display = ['maintenance_mode_display', 'kyc_required_display']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Feature Flags', {
            'fields': (
                'maintenance_mode',
                'kyc_required',
                'kyc_auto_approve_documents',
                'enable_bot_trading'
            )
        }),
        ('Fees & Limits', {
            'fields': (
                'platform_fee_percentage',
                'minimum_investment',
                'maximum_investment',
                'minimum_withdrawal',
                'maximum_withdrawal'
            )
        }),
        ('Integration Status', {
            'fields': (
                'mpesa_enabled',
                'crypto_enabled',
                'email_notifications_enabled',
                'sms_notifications_enabled'
            )
        }),
        ('Security', {
            'fields': ('kyc_auto_verify_threshold', 'max_login_attempts')
        }),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    def maintenance_mode_display(self, obj):
        if obj.maintenance_mode:
            return format_html('<span style="color: red;">🔴 Maintenance Mode ON</span>')
        return format_html('<span style="color: green;">🟢 Normal Operation</span>')
    maintenance_mode_display.short_description = 'System Status'

    def kyc_required_display(self, obj):
        if obj.kyc_required:
            return format_html('<span style="color: blue;">✓ KYC Required</span>')
        return format_html('<span style="color: gray;">- KYC Optional</span>')
    kyc_required_display.short_description = 'KYC Status'
