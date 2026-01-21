from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class KYCDocument(models.Model):
    """KYC document submissions and verification"""
    KYC_TYPES = [
        ('national_id', 'National ID'),
        ('passport', 'Passport'),
        ('drivers_license', 'Driver\'s License'),
    ]
    
    KYC_STATUS = [
        ('not_started', 'Not Started'),
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='kyc_document')
    
    # Personal Information
    full_name = models.CharField(max_length=200)
    date_of_birth = models.DateField()
    nationality = models.CharField(max_length=100)
    
    # Document Information
    document_type = models.CharField(max_length=20, choices=KYC_TYPES)
    document_number = models.CharField(max_length=100, unique=True)
    document_front_url = models.URLField(null=True, blank=True)  # S3/Cloudinary URL
    document_back_url = models.URLField(null=True, blank=True)
    
    # Address Information
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state_province = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    address_proof_url = models.URLField(null=True, blank=True)  # Utility bill, rental agreement, etc
    
    # Selfie/Proof of Life
    selfie_url = models.URLField(null=True, blank=True)
    selfie_timestamp = models.DateTimeField(null=True, blank=True)
    
    # Verification Status
    status = models.CharField(max_length=20, choices=KYC_STATUS, default='not_started')
    verification_level = models.IntegerField(default=1)  # 1=Basic, 2=Enhanced, 3=Full
    
    # Verification Details
    verified_by = models.ForeignKey('admin_panel.AdminUser', on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='kyc_verified')
    verification_date = models.DateTimeField(null=True, blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    
    # Timestamps
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"KYC - {self.user.user_id}"
    
    @property
    def is_expired(self):
        if self.expiry_date and timezone.now() > self.expiry_date:
            return True
        return False
    
    @property
    def needs_resubmission(self):
        return self.status in ['rejected', 'expired']
    
    class Meta:
        db_table = 'kyc_kydocument'
        verbose_name = 'KYC Document'
        verbose_name_plural = 'KYC Documents'
        ordering = ['-submitted_at']


class KYCVerificationLog(models.Model):
    """Log of all KYC verification actions"""
    ACTION_TYPES = [
        ('submitted', 'Document Submitted'),
        ('auto_approved', 'Auto Approved'),
        ('manual_approved', 'Manually Approved'),
        ('requested_resubmit', 'Requested Resubmission'),
        ('rejected', 'Rejected'),
        ('expired', 'Marked as Expired'),
    ]
    
    kyc = models.ForeignKey(KYCDocument, on_delete=models.CASCADE, related_name='verification_logs')
    action = models.CharField(max_length=20, choices=ACTION_TYPES)
    performed_by = models.ForeignKey('admin_panel.AdminUser', on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='kyc_actions')
    notes = models.TextField(blank=True)
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    verification_score = models.FloatField(null=True, blank=True)  # 0-100, auto-verification score
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.kyc.user.user_id} - {self.action} - {self.created_at}"
    
    class Meta:
        db_table = 'kyc_kycverificationlog'
        verbose_name = 'KYC Verification Log'
        verbose_name_plural = 'KYC Verification Logs'
        ordering = ['-created_at']


class KYCRejectionTemplate(models.Model):
    """Pre-defined KYC rejection templates"""
    code = models.CharField(max_length=50, unique=True)  # e.g., 'BLURRY_DOCUMENT'
    title = models.CharField(max_length=200)
    message = models.TextField()
    category = models.CharField(max_length=50, choices=[
        ('document_quality', 'Document Quality'),
        ('information_mismatch', 'Information Mismatch'),
        ('expired_document', 'Expired Document'),
        ('suspicious_activity', 'Suspicious Activity'),
        ('other', 'Other'),
    ])
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        db_table = 'kyc_rejectiontemplate'
        verbose_name = 'KYC Rejection Template'
        verbose_name_plural = 'KYC Rejection Templates'


class KYCWithdrawalLimit(models.Model):
    """Define withdrawal limits based on KYC verification level"""
    VERIFICATION_LEVELS = [
        (1, 'Level 1 - Basic'),
        (2, 'Level 2 - Enhanced'),
        (3, 'Level 3 - Full'),
    ]
    
    verification_level = models.IntegerField(choices=VERIFICATION_LEVELS, unique=True)
    daily_limit = models.DecimalField(max_digits=15, decimal_places=2)
    monthly_limit = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_limit = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField()
    
    def __str__(self):
        return f"Level {self.verification_level} Limits"
    
    class Meta:
        db_table = 'kyc_withdrawallimit'
        verbose_name = 'KYC Withdrawal Limit'
        verbose_name_plural = 'KYC Withdrawal Limits'
