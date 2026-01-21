from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import AdminUser, AdminLog, PlatformStatistics, SystemConfiguration
from apps.users.models import User as UserModel
from apps.payments.models import Balance, Transaction, Deposit, Withdrawal
from apps.investments.models import Investment

User = get_user_model()


class AdminUserSerializer(serializers.ModelSerializer):
    """Serializer for admin users"""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = AdminUser
        fields = ['id', 'username', 'email', 'role', 'is_active', 'can_suspend_users',
                  'can_adjust_transactions', 'can_verify_kyc', 'can_manage_admins',
                  'last_login', 'created_at']
        read_only_fields = ['created_at', 'last_login']


class AdminLogSerializer(serializers.ModelSerializer):
    """Serializer for admin audit logs"""
    admin_username = serializers.CharField(source='admin.user.username', read_only=True)
    affected_user_id = serializers.CharField(source='affected_user.user_id', read_only=True)
    
    class Meta:
        model = AdminLog
        fields = ['id', 'admin_username', 'action_type', 'affected_user_id', 'resource_type',
                  'resource_id', 'reason', 'old_value', 'new_value', 'ip_address', 'created_at']
        read_only_fields = ['created_at']


class PlatformStatisticsSerializer(serializers.ModelSerializer):
    """Serializer for platform statistics"""
    class Meta:
        model = PlatformStatistics
        fields = ['id', 'date', 'total_users', 'active_users', 'suspended_users',
                  'total_deposited', 'total_withdrawn', 'total_profit_generated',
                  'total_fees_collected', 'assets_under_management', 'total_transactions',
                  'new_deposits', 'new_withdrawals', 'kyc_verified', 'kyc_pending',
                  'kyc_rejected', 'created_at', 'updated_at']
        read_only_fields = ['date', 'created_at', 'updated_at']


class SystemConfigurationSerializer(serializers.ModelSerializer):
    """Serializer for system configuration"""
    class Meta:
        model = SystemConfiguration
        fields = ['id', 'platform_name', 'platform_fee_percent', 'minimum_deposit',
                  'maximum_withdrawal', 'deposits_enabled', 'withdrawals_enabled',
                  'referrals_enabled', 'kyc_required_for_withdrawal', 'bot_trading_enabled',
                  'mpesa_enabled', 'crypto_enabled', 'email_notifications_enabled',
                  'sms_notifications_enabled', 'kyc_verification_level',
                  'kyc_auto_approve_documents', 'kyc_expiry_months', 'max_login_attempts',
                  'login_lockout_minutes', 'force_2fa', 'sentry_enabled',
                  'health_check_enabled', 'updated_at']


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for admin dashboard statistics"""
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    total_deposited = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_withdrawn = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_profit = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_fees = serializers.DecimalField(max_digits=15, decimal_places=2)
    assets_under_management = serializers.DecimalField(max_digits=15, decimal_places=2)
    pending_withdrawals = serializers.IntegerField()
    pending_kyc = serializers.IntegerField()
    active_investments = serializers.IntegerField()


class UserManagementSerializer(serializers.ModelSerializer):
    """Serializer for user management"""
    balance = serializers.SerializerMethodField()
    total_deposited = serializers.SerializerMethodField()
    total_profit = serializers.SerializerMethodField()
    investment_count = serializers.SerializerMethodField()
    account_status = serializers.CharField(source='account_status', read_only=True)
    
    class Meta:
        model = UserModel
        fields = ['id', 'user_id', 'username', 'email', 'account_status', 'balance',
                  'total_deposited', 'total_profit', 'investment_count', 'created_at']
        read_only_fields = ['user_id', 'created_at']
    
    def get_balance(self, obj):
        try:
            balance_obj = Balance.objects.get(user=obj)
            return str(balance_obj.current_balance)
        except Balance.DoesNotExist:
            return "0.00"
    
    def get_total_deposited(self, obj):
        try:
            balance_obj = Balance.objects.get(user=obj)
            return str(balance_obj.total_deposited)
        except Balance.DoesNotExist:
            return "0.00"
    
    def get_total_profit(self, obj):
        try:
            balance_obj = Balance.objects.get(user=obj)
            return str(balance_obj.total_profit)
        except Balance.DoesNotExist:
            return "0.00"
    
    def get_investment_count(self, obj):
        return Investment.objects.filter(user=obj, status='active').count()


class PendingWithdrawalSerializer(serializers.ModelSerializer):
    """Serializer for pending withdrawals"""
    user_id = serializers.CharField(source='user.user_id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Withdrawal
        fields = ['id', 'user_id', 'username', 'amount', 'payment_method', 'status',
                  'created_at', 'reference']
        read_only_fields = ['created_at']
