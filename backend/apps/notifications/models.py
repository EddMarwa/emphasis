from django.db import models
from apps.users.models import User


class Notification(models.Model):
    """System notifications for users"""
    TYPE_CHOICES = [
        ('deposit_confirmation', 'Deposit Confirmation'),
        ('withdrawal_confirmation', 'Withdrawal Confirmation'),
        ('profit_update', 'Profit Update'),
        ('referral_bonus', 'Referral Bonus'),
        ('security_alert', 'Security Alert'),
        ('kyc_update', 'KYC Update'),
        ('system_announcement', 'System Announcement'),
        ('general', 'General'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    sent_via_email = models.BooleanField(default=False)
    sent_via_sms = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Optional metadata (JSON serialized)
    metadata = models.JSONField(null=True, blank=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['type', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.user_id} - {self.type} - {self.title}"


class NotificationPreference(models.Model):
    """User notification preferences"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Email preferences
    email_deposit = models.BooleanField(default=True)
    email_withdrawal = models.BooleanField(default=True)
    email_profit = models.BooleanField(default=True)
    email_referral = models.BooleanField(default=True)
    email_security = models.BooleanField(default=True)
    email_kyc = models.BooleanField(default=True)
    email_system = models.BooleanField(default=True)
    
    # SMS preferences
    sms_deposit = models.BooleanField(default=False)
    sms_withdrawal = models.BooleanField(default=True)
    sms_security = models.BooleanField(default=True)
    
    # In-app preferences
    inapp_all = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_preferences'
    
    def __str__(self):
        return f"{self.user.user_id} - Notification Preferences"
