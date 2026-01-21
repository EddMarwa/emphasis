from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class AdminUser(models.Model):
    """Admin user accounts with role-based access"""
    ROLE_CHOICES = [
        ('superadmin', 'Super Admin - Full Access'),
        ('admin', 'Admin - Platform Management'),
        ('moderator', 'Moderator - User Support'),
        ('analyst', 'Analyst - Reporting Only'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='moderator')
    is_active = models.BooleanField(default=True)
    can_suspend_users = models.BooleanField(default=False)
    can_adjust_transactions = models.BooleanField(default=False)
    can_verify_kyc = models.BooleanField(default=False)
    can_manage_admins = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    def save(self, *args, **kwargs):
        # Set permissions based on role
        if self.role == 'superadmin':
            self.can_suspend_users = True
            self.can_adjust_transactions = True
            self.can_verify_kyc = True
            self.can_manage_admins = True
        elif self.role == 'admin':
            self.can_suspend_users = True
            self.can_adjust_transactions = True
            self.can_verify_kyc = True
            self.can_manage_admins = False
        elif self.role == 'moderator':
            self.can_suspend_users = False
            self.can_adjust_transactions = False
            self.can_verify_kyc = True
            self.can_manage_admins = False
        elif self.role == 'analyst':
            self.can_suspend_users = False
            self.can_adjust_transactions = False
            self.can_verify_kyc = False
            self.can_manage_admins = False
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'admin_adminuser'
        verbose_name = 'Admin User'
        verbose_name_plural = 'Admin Users'


class AdminLog(models.Model):
    """Audit log for all admin actions"""
    ACTION_TYPES = [
        ('suspend_user', 'Suspend User'),
        ('activate_user', 'Activate User'),
        ('adjust_transaction', 'Adjust Transaction'),
        ('verify_kyc', 'Verify KYC'),
        ('reject_kyc', 'Reject KYC'),
        ('approve_withdrawal', 'Approve Withdrawal'),
        ('reject_withdrawal', 'Reject Withdrawal'),
        ('adjust_balance', 'Adjust Balance'),
        ('create_admin', 'Create Admin User'),
        ('delete_admin', 'Delete Admin User'),
        ('change_permission', 'Change Permission'),
        ('export_report', 'Export Report'),
        ('system_config', 'System Configuration'),
    ]

    admin = models.ForeignKey(AdminUser, on_delete=models.SET_NULL, null=True, related_name='logs')
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    affected_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_logs')
    resource_id = models.IntegerField(null=True, blank=True)  # ID of affected resource (transaction, kyc, etc)
    resource_type = models.CharField(max_length=50, blank=True)  # Type of resource (transaction, kyc, withdrawal, etc)
    old_value = models.JSONField(null=True, blank=True)  # Previous value
    new_value = models.JSONField(null=True, blank=True)  # New value
    reason = models.TextField(blank=True)  # Reason for action
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.admin.user.username} - {self.action_type} - {self.created_at}"

    class Meta:
        db_table = 'admin_adminlog'
        verbose_name = 'Admin Log'
        verbose_name_plural = 'Admin Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['admin', '-created_at']),
            models.Index(fields=['affected_user', '-created_at']),
            models.Index(fields=['action_type', '-created_at']),
        ]


class PlatformStatistics(models.Model):
    """Daily platform statistics for analytics"""
    date = models.DateField(auto_now_add=True, unique=True)
    total_users = models.IntegerField(default=0)
    active_users = models.IntegerField(default=0)
    suspended_users = models.IntegerField(default=0)
    total_deposited = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_withdrawn = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_profit_generated = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_fees_collected = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    assets_under_management = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_transactions = models.IntegerField(default=0)
    new_deposits = models.IntegerField(default=0)
    new_withdrawals = models.IntegerField(default=0)
    kyc_verified = models.IntegerField(default=0)
    kyc_pending = models.IntegerField(default=0)
    kyc_rejected = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Statistics - {self.date}"

    class Meta:
        db_table = 'admin_platformstatistics'
        verbose_name = 'Platform Statistics'
        verbose_name_plural = 'Platform Statistics'
        ordering = ['-date']


class SystemConfiguration(models.Model):
    """Platform-wide configuration settings"""
    # Platform Settings
    platform_name = models.CharField(max_length=100, default='Quantum Capital')
    platform_fee_percent = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    minimum_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=10000)
    maximum_withdrawal = models.DecimalField(max_digits=10, decimal_places=2, default=500000)
    
    # Feature Flags
    deposits_enabled = models.BooleanField(default=True)
    withdrawals_enabled = models.BooleanField(default=True)
    referrals_enabled = models.BooleanField(default=True)
    kyc_required_for_withdrawal = models.BooleanField(default=True)
    bot_trading_enabled = models.BooleanField(default=True)
    
    # External Integration Status
    mpesa_enabled = models.BooleanField(default=False)
    crypto_enabled = models.BooleanField(default=False)
    email_notifications_enabled = models.BooleanField(default=False)
    sms_notifications_enabled = models.BooleanField(default=False)
    
    # KYC Settings
    kyc_verification_level = models.IntegerField(default=1)  # 1-3 levels
    kyc_auto_approve_documents = models.BooleanField(default=False)
    kyc_expiry_months = models.IntegerField(default=12)
    
    # Security Settings
    max_login_attempts = models.IntegerField(default=5)
    login_lockout_minutes = models.IntegerField(default=30)
    force_2fa = models.BooleanField(default=False)
    
    # Monitoring
    sentry_enabled = models.BooleanField(default=False)
    health_check_enabled = models.BooleanField(default=False)
    
    last_updated_by = models.ForeignKey(AdminUser, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"System Config - {self.platform_name}"

    class Meta:
        db_table = 'admin_systemconfiguration'
        verbose_name = 'System Configuration'
        verbose_name_plural = 'System Configuration'
        
    @classmethod
    def get_config(cls):
        """Get or create singleton config"""
        config, created = cls.objects.get_or_create(id=1)
        return config
