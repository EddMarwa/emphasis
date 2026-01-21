from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'email', 'first_name', 'last_name', 'country_code', 'account_status', 'created_at')
    list_filter = ('account_status', 'kyc_status', 'country_code', 'created_at')
    search_fields = ('user_id', 'email', 'first_name', 'last_name', 'phone')
    readonly_fields = ('user_id', 'referral_code', 'created_at', 'updated_at', 'last_login')
    fieldsets = (
        ('User Information', {
            'fields': ('user_id', 'email', 'phone', 'first_name', 'last_name', 'country_code')
        }),
        ('Account Status', {
            'fields': ('account_status', 'kyc_status', 'email_verified', 'phone_verified')
        }),
        ('Security', {
            'fields': ('password_hash',)
        }),
        ('Referral', {
            'fields': ('referral_code', 'referred_by')
        }),
        ('Additional Info', {
            'fields': ('date_of_birth', 'profile_picture', 'created_at', 'updated_at', 'last_login')
        }),
    )

