from django.contrib import admin
from .models import KYCDocument, KYCVerificationLog, KYCRejectionTemplate, KYCWithdrawalLimit


@admin.register(KYCDocument)
class KYCDocumentAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'verification_level', 'created_at']
    list_filter = ['status', 'verification_level', 'created_at']
    search_fields = ['user__username', 'user__email', 'full_name']
    readonly_fields = ['created_at', 'updated_at', 'auto_verified', 'verification_score']
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
                'auto_verified',
                'verification_score',
                'expiry_date'
            )
        }),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(KYCVerificationLog)
class KYCVerificationLogAdmin(admin.ModelAdmin):
    list_display = ['kyc_document', 'action_type', 'verified_by', 'timestamp']
    list_filter = ['action_type', 'timestamp']
    search_fields = ['kyc_document__user__username', 'verified_by__username']
    readonly_fields = ['timestamp']
    fieldsets = (
        ('KYC Document', {'fields': ('kyc_document',)}),
        ('Verification', {
            'fields': (
                'action_type',
                'verification_score',
                'verified_by'
            )
        }),
        ('Notes', {'fields': ('verification_notes',)}),
        ('Timestamp', {'fields': ('timestamp',)}),
    )


@admin.register(KYCRejectionTemplate)
class KYCRejectionTemplateAdmin(admin.ModelAdmin):
    list_display = ['reason_type', 'is_active']
    list_filter = ['reason_type', 'is_active']
    readonly_fields = ['created_at']
    fieldsets = (
        ('Template Info', {'fields': ('reason_type', 'is_active')}),
        ('Content', {'fields': ('template_message',)}),
        ('Timestamp', {'fields': ('created_at',)}),
    )


@admin.register(KYCWithdrawalLimit)
class KYCWithdrawalLimitAdmin(admin.ModelAdmin):
    list_display = ['verification_level', 'daily_limit', 'monthly_limit']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Level', {'fields': ('verification_level',)}),
        ('Daily Limit', {'fields': ('daily_limit',)}),
        ('Monthly Limit', {'fields': ('monthly_limit',)}),
        ('Per Transaction Limit', {'fields': ('per_transaction_limit',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
