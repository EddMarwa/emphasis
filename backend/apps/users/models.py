from django.db import models
from django.contrib.auth.hashers import make_password, check_password
import random
import string

class User(models.Model):
    user_id = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, unique=True)
    password_hash = models.CharField(max_length=255)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    country_code = models.CharField(max_length=5, default='KE')
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.CharField(max_length=255, null=True, blank=True)
    
    ACCOUNT_STATUS_CHOICES = [
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('pending', 'Pending'),
        ('closed', 'Closed'),
    ]
    account_status = models.CharField(max_length=20, choices=ACCOUNT_STATUS_CHOICES, default='active')
    
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)

    # Two-factor auth (TOTP)
    otp_secret = models.CharField(max_length=32, null=True, blank=True)
    otp_enabled = models.BooleanField(default=False)
    
    KYC_STATUS_CHOICES = [
        ('unverified', 'Unverified'),
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]
    kyc_status = models.CharField(max_length=20, choices=KYC_STATUS_CHOICES, default='unverified')
    
    referral_code = models.CharField(max_length=20, unique=True)
    referred_by = models.CharField(max_length=20, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'users'
    
    def set_password(self, raw_password):
        self.password_hash = make_password(raw_password)
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.password_hash)
    
    @staticmethod
    def generate_user_id(country_code='KE'):
        """
        Generate user ID based on country code.
        Format: {COUNTRY_CODE}-QC-{NUMBER}
        Example: KE-QC-00001, US-QC-00001
        """
        # Get the last user with the same country code
        last_user = User.objects.filter(country_code=country_code).order_by('-id').first()
        if last_user and last_user.user_id:
            try:
                # Extract the number from user_id (e.g., "KE-QC-00001" -> 1)
                parts = last_user.user_id.split('-')
                if len(parts) >= 3:
                    last_number = int(parts[-1])
                    new_number = last_number + 1
                else:
                    new_number = 1
            except (ValueError, IndexError):
                new_number = 1
        else:
            new_number = 1
        return f"{country_code}-QC-{str(new_number).zfill(5)}"
    
    @staticmethod
    def generate_referral_code():
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    def __str__(self):
        return f"{self.user_id} - {self.email}"


class LoginHistory(models.Model):
    """Track all user login attempts"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_history')
    login_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    success = models.BooleanField(default=True)
    device_info = models.CharField(max_length=255, blank=True)
    
    class Meta:
        db_table = 'login_history'
        ordering = ['-login_time']
        indexes = [
            models.Index(fields=['user', '-login_time']),
            models.Index(fields=['-login_time']),
        ]
    
    def __str__(self):
        return f"{self.user.user_id} - {self.login_time} - {'Success' if self.success else 'Failed'}"


class FailedLoginAttempt(models.Model):
    """Track failed login attempts for security monitoring"""
    email_or_user_id = models.CharField(max_length=255)
    attempt_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    reason = models.CharField(max_length=100, choices=[
        ('invalid_credentials', 'Invalid Credentials'),
        ('account_suspended', 'Account Suspended'),
        ('account_inactive', 'Account Inactive'),
        ('invalid_2fa', 'Invalid 2FA Code'),
        ('user_not_found', 'User Not Found'),
    ])
    
    class Meta:
        db_table = 'failed_login_attempts'
        ordering = ['-attempt_time']
        indexes = [
            models.Index(fields=['-attempt_time']),
            models.Index(fields=['ip_address', '-attempt_time']),
        ]
    
    def __str__(self):
        return f"{self.email_or_user_id} - {self.attempt_time} - {self.reason}"


class DeviceTracking(models.Model):
    """Track user devices for security"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devices')
    device_id = models.CharField(max_length=255, unique=True)  # Generated hash
    device_name = models.CharField(max_length=255, blank=True)  # e.g., "Chrome on Windows"
    device_type = models.CharField(max_length=50, choices=[
        ('desktop', 'Desktop'),
        ('mobile', 'Mobile'),
        ('tablet', 'Tablet'),
        ('unknown', 'Unknown'),
    ], default='unknown')
    user_agent = models.CharField(max_length=500, blank=True)
    browser = models.CharField(max_length=100, blank=True)
    os = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    last_used_ip = models.GenericIPAddressField(null=True, blank=True)
    is_trusted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'device_tracking'
        ordering = ['-last_seen']
        indexes = [
            models.Index(fields=['user', '-last_seen']),
            models.Index(fields=['device_id']),
        ]
    
    def __str__(self):
        return f"{self.user.user_id} - {self.device_name or self.device_type}"


class SecurityLog(models.Model):
    """Log security events"""
    EVENT_TYPES = [
        ('password_changed', 'Password Changed'),
        ('email_changed', 'Email Changed'),
        ('phone_changed', 'Phone Changed'),
        ('2fa_enabled', '2FA Enabled'),
        ('2fa_disabled', '2FA Disabled'),
        ('unusual_login', 'Unusual Login Activity'),
        ('account_locked', 'Account Locked'),
        ('account_unlocked', 'Account Unlocked'),
        ('suspicious_activity', 'Suspicious Activity Detected'),
        ('new_device', 'New Device Detected'),
        ('device_removed', 'Device Removed'),
        ('multiple_failed_logins', 'Multiple Failed Logins'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='security_logs')
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    device = models.ForeignKey(DeviceTracking, on_delete=models.SET_NULL, null=True, blank=True, related_name='security_logs')
    severity = models.CharField(max_length=20, choices=[
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ], default='info')
    alert_sent = models.BooleanField(default=False)  # Email/SMS sent
    alert_sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'security_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['event_type', '-created_at']),
            models.Index(fields=['severity', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.user_id} - {self.event_type} - {self.severity}"

