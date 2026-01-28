from rest_framework import serializers
from .models import Referral, ReferralBonus, ReferralLeaderboard, ReferralAnalytics, ReferralProgram
from apps.users.models import User


class ReferralProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferralProgram
        fields = '__all__'


class ReferralSerializer(serializers.ModelSerializer):
    referrer_id = serializers.CharField(source='referrer.user_id', read_only=True)
    referee_id = serializers.CharField(source='referee.user_id', read_only=True)
    referee_email = serializers.CharField(source='referee.email', read_only=True)
    referee_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Referral
        fields = ['id', 'referrer_id', 'referee_id', 'referee_email', 'referee_name',
                 'referral_code_used', 'tier_level', 'status', 'first_deposit_made',
                 'first_deposit_amount', 'first_deposit_date', 'referee_bonus_given',
                 'referrer_bonus_given', 'created_at', 'activated_at']
    
    def get_referee_name(self, obj):
        return f"{obj.referee.first_name} {obj.referee.last_name}"


class ReferralBonusSerializer(serializers.ModelSerializer):
    recipient_id = serializers.CharField(source='recipient.user_id', read_only=True)
    
    class Meta:
        model = ReferralBonus
        fields = ['id', 'recipient_id', 'bonus_type', 'amount', 'status',
                 'description', 'distributed_at', 'expires_at', 'created_at']


class ReferralLeaderboardSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(source='user.user_id', read_only=True)
    
    class Meta:
        model = ReferralLeaderboard
        fields = ['rank', 'user_id', 'period_type', 'total_referrals', 'active_referrals',
                 'total_bonus_earned', 'tier1_referrals', 'tier2_referrals', 'tier3_referrals',
                 'points', 'prize_awarded', 'prize_amount', 'prize_description']


class ReferralAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferralAnalytics
        fields = ['date', 'new_referrals', 'activated_referrals', 'bonuses_earned',
                 'bonuses_distributed', 'total_referrals', 'total_active_referrals',
                 'total_bonuses_earned', 'total_bonuses_pending']


class ReferralStatsSerializer(serializers.Serializer):
    """Summary statistics for user referrals"""
    total_referrals = serializers.IntegerField()
    active_referrals = serializers.IntegerField()
    pending_referrals = serializers.IntegerField()
    total_bonuses_earned = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_bonuses_pending = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_bonuses_distributed = serializers.DecimalField(max_digits=12, decimal_places=2)
    referral_code = serializers.CharField()
    referral_link = serializers.CharField()
    tier1_count = serializers.IntegerField()
    tier2_count = serializers.IntegerField()
    tier3_count = serializers.IntegerField()
