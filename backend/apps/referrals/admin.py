from django.contrib import admin
from .models import ReferralProgram, Referral, ReferralBonus, ReferralLeaderboard, ReferralAnalytics


@admin.register(ReferralProgram)
class ReferralProgramAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'referee_bonus_amount', 'referrer_bonus_amount', 'enable_multi_tier']
    list_filter = ['is_active', 'enable_multi_tier']
    search_fields = ['name']


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ['referrer', 'referee', 'tier_level', 'status', 'first_deposit_made', 'created_at']
    list_filter = ['status', 'tier_level', 'first_deposit_made']
    search_fields = ['referrer__user_id', 'referee__user_id', 'referral_code_used']
    date_hierarchy = 'created_at'


@admin.register(ReferralBonus)
class ReferralBonusAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'bonus_type', 'amount', 'status', 'created_at']
    list_filter = ['status', 'bonus_type']
    search_fields = ['recipient__user_id']
    date_hierarchy = 'created_at'


@admin.register(ReferralLeaderboard)
class ReferralLeaderboardAdmin(admin.ModelAdmin):
    list_display = ['rank', 'user', 'period_type', 'total_referrals', 'total_bonus_earned', 'points']
    list_filter = ['period_type', 'prize_awarded']
    search_fields = ['user__user_id']
    ordering = ['period_type', 'rank']


@admin.register(ReferralAnalytics)
class ReferralAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'new_referrals', 'total_referrals', 'bonuses_earned']
    list_filter = ['date']
    search_fields = ['user__user_id']
    date_hierarchy = 'date'
