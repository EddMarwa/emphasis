from django.contrib import admin
from .models import KYCDocument, KYCVerificationLog, KYCRejectionTemplate, KYCWithdrawalLimit


@admin.register(KYCDocument)
class KYCDocumentAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'verification_level', 'submitted_at']
    list_filter = ['status', 'verification_level', 'submitted_at']
    search_fields = ['user__username', 'user__email', 'full_name']
    readonly_fields = ['submitted_at', 'updated_at']
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Personal Information', {
            'fields': (
                'full_name',
                'date_of_birth',
                'nationality',
                'document_type'
            )
        }),
        ('Documents', {
            'fields': (
                'document_front_url',
                'document_back_url',
                'address_proof_url',
                'selfie_url'
            )
        }),
        ('Address Information', {
            'fields': (
                'country',
                'state_province',
                'city',
                'postal_code'
            )
        }),
        ('Verification Status', {
            'fields': (
                'status',
                'verification_level',
                'verified_by',
                'verification_date',
                'expiry_date'
            )
        }),
        ('Timestamps', {'fields': ('submitted_at', 'updated_at')}),
    )


@admin.register(KYCVerificationLog)
class KYCVerificationLogAdmin(admin.ModelAdmin):
    list_display = ['kyc', 'action', 'performed_by', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['kyc__user__username']
    readonly_fields = ['created_at']
    fieldsets = (
        ('KYC Document', {'fields': ('kyc',)}),
        ('Verification', {
            'fields': (
                'action',
                'verification_score',
                'performed_by'
            )
        }),
        ('Status Change', {'fields': ('old_status', 'new_status')}),
        ('Notes', {'fields': ('notes',)}),
        ('Timestamp', {'fields': ('created_at',)}),
    )


@admin.register(KYCRejectionTemplate)
class KYCRejectionTemplateAdmin(admin.ModelAdmin):
    list_display = ['code', 'title', 'category', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['code', 'title', 'message']
    fieldsets = (
        ('Template Info', {'fields': ('code', 'title', 'category', 'is_active')}),
        ('Content', {'fields': ('message',)}),
    )


@admin.register(KYCWithdrawalLimit)
class KYCWithdrawalLimitAdmin(admin.ModelAdmin):
    list_display = ['verification_level', 'daily_limit', 'monthly_limit']
    readonly_fields = ['verification_level']
    fieldsets = (
        ('Level', {'fields': ('verification_level',)}),
        ('Limits', {'fields': ('daily_limit', 'monthly_limit', 'transaction_limit')}),
    )
