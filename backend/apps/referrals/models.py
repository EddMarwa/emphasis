from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal

User = get_user_model()


class ReferralProgram(models.Model):
    """Referral program configuration"""
    name = models.CharField(max_length=100, default='Default Program')
    is_active = models.BooleanField(default=True)
    
    # Bonus Structure
    referee_bonus_amount = models.DecimalField(max_digits=10, decimal_places=2, default=500.00,
                                               help_text='Bonus for new user who signs up')
    referrer_bonus_amount = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00,
                                                help_text='Bonus for existing user who referred')
    referrer_bonus_percent = models.DecimalField(max_digits=5, decimal_places=2, default=5.00,
                                                 help_text='Percentage of referee first deposit')
    
    # Multi-tier Settings
    enable_multi_tier = models.BooleanField(default=True)
    tier2_bonus_percent = models.DecimalField(max_digits=5, decimal_places=2, default=2.00,
                                             help_text='% bonus for tier 2 referrals')
    tier3_bonus_percent = models.DecimalField(max_digits=5, decimal_places=2, default=1.00,
                                             help_text='% bonus for tier 3 referrals')
    
    # Requirements
    minimum_deposit_required = models.DecimalField(max_digits=10, decimal_places=2, default=5000.00,
                                                   help_text='Min deposit for referee to activate bonus')
    bonus_expiry_days = models.IntegerField(default=90, help_text='Days before bonus expires')
    
    # Limits
    max_referrals_per_user = models.IntegerField(default=0, help_text='0 = unlimited')
    max_bonus_per_referral = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                                 help_text='0 = unlimited')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'referrals_program'
        verbose_name = 'Referral Program'
        verbose_name_plural = 'Referral Programs'
    
    def __str__(self):
        return f"{self.name} ({'Active' if self.is_active else 'Inactive'})"
    
    @classmethod
    def get_active_program(cls):
        """Get the active referral program"""
        return cls.objects.filter(is_active=True).first()


class Referral(models.Model):
    """Track referral relationships"""
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_made')
    referee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referred_by_user')
    referral_code_used = models.CharField(max_length=20)
    
    # Tier tracking
    tier_level = models.IntegerField(default=1, help_text='1=direct, 2=indirect, 3=3rd level')
    parent_referral = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='sub_referrals')
    
    # Status
    STATUS_CHOICES = [
        ('pending', 'Pending - Awaiting deposit'),
        ('active', 'Active - Bonus earned'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Tracking
    first_deposit_made = models.BooleanField(default=False)
    first_deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    first_deposit_date = models.DateTimeField(null=True, blank=True)
    
    # Bonuses
    referee_bonus_given = models.BooleanField(default=False)
    referrer_bonus_given = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    activated_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'referrals'
        verbose_name = 'Referral'
        verbose_name_plural = 'Referrals'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['referrer', '-created_at']),
            models.Index(fields=['referee']),
            models.Index(fields=['status']),
        ]
        unique_together = [['referrer', 'referee']]
    
    def __str__(self):
        return f"{self.referrer.user_id} → {self.referee.user_id} (Tier {self.tier_level})"


class ReferralBonus(models.Model):
    """Track individual bonus distributions"""
    referral = models.ForeignKey(Referral, on_delete=models.CASCADE, related_name='bonuses')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referral_bonuses')
    
    BONUS_TYPE_CHOICES = [
        ('signup', 'Sign-up Bonus'),
        ('deposit', 'Deposit Bonus'),
        ('tier1', 'Tier 1 Bonus'),
        ('tier2', 'Tier 2 Bonus'),
        ('tier3', 'Tier 3 Bonus'),
        ('special', 'Special Bonus'),
    ]
    bonus_type = models.CharField(max_length=20, choices=BONUS_TYPE_CHOICES)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('distributed', 'Distributed'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    description = models.TextField(blank=True)
    distributed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'referral_bonuses'
        verbose_name = 'Referral Bonus'
        verbose_name_plural = 'Referral Bonuses'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.recipient.user_id} - {self.bonus_type} - {self.amount} KES"


class ReferralLeaderboard(models.Model):
    """Leaderboard rankings for referrals"""
    PERIOD_CHOICES = [
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
        ('all_time', 'All Time'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leaderboard_entries')
    period_type = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Metrics
    total_referrals = models.IntegerField(default=0)
    active_referrals = models.IntegerField(default=0)
    total_bonus_earned = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tier1_referrals = models.IntegerField(default=0)
    tier2_referrals = models.IntegerField(default=0)
    tier3_referrals = models.IntegerField(default=0)
    
    # Ranking
    rank = models.IntegerField(default=0)
    points = models.IntegerField(default=0, help_text='Points for gamification')
    
    # Rewards
    prize_awarded = models.BooleanField(default=False)
    prize_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    prize_description = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'referral_leaderboard'
        verbose_name = 'Referral Leaderboard'
        verbose_name_plural = 'Referral Leaderboards'
        ordering = ['period_type', '-points', '-total_referrals']
        indexes = [
            models.Index(fields=['period_type', '-rank']),
            models.Index(fields=['user', 'period_type']),
        ]
        unique_together = [['user', 'period_type', 'period_start', 'period_end']]
    
    def __str__(self):
        return f"Rank #{self.rank} - {self.user.user_id} ({self.period_type})"
    
    def calculate_points(self):
        """Calculate points based on referral activity"""
        # 10 points per active referral
        # 5 points per tier 2 referral
        # 2 points per tier 3 referral
        # Bonus points for high earners
        self.points = (
            (self.active_referrals * 10) +
            (self.tier2_referrals * 5) +
            (self.tier3_referrals * 2) +
            int(self.total_bonus_earned / 1000)  # 1 point per 1000 KES earned
        )
        return self.points


class ReferralAnalytics(models.Model):
    """Daily analytics for referral performance"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referral_analytics')
    date = models.DateField(auto_now_add=True)
    
    # Daily metrics
    new_referrals = models.IntegerField(default=0)
    activated_referrals = models.IntegerField(default=0)
    bonuses_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bonuses_distributed = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Cumulative metrics
    total_referrals = models.IntegerField(default=0)
    total_active_referrals = models.IntegerField(default=0)
    total_bonuses_earned = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_bonuses_pending = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'referral_analytics'
        verbose_name = 'Referral Analytics'
        verbose_name_plural = 'Referral Analytics'
        ordering = ['-date']
        indexes = [
            models.Index(fields=['user', '-date']),
        ]
        unique_together = [['user', 'date']]
    
    def __str__(self):
        return f"{self.user.user_id} - {self.date}"
