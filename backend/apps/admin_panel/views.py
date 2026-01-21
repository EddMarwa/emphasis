from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q, Count, Sum
from django.contrib.auth import get_user_model
from django.http import HttpResponse
import csv
from datetime import datetime, timedelta

from .models import AdminUser, AdminLog, PlatformStatistics, SystemConfiguration
from .serializers import (
    AdminUserSerializer, AdminLogSerializer, PlatformStatisticsSerializer,
    SystemConfigurationSerializer, DashboardStatsSerializer,
    UserManagementSerializer, PendingWithdrawalSerializer
)
from apps.payments.models import Balance, Transaction, Withdrawal, Deposit
from apps.investments.models import Investment
from apps.users.models import User as UserModel

User = get_user_model()


class IsAdmin(IsAuthenticated):
    """Permission to check if user is admin"""
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        try:
            AdminUser.objects.get(user=request.user, is_active=True)
            return True
        except AdminUser.DoesNotExist:
            return False


class AdminDashboardView(viewsets.ViewSet):
    """Admin dashboard statistics and overview"""
    permission_classes = [IsAdmin]
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get platform statistics"""
        # User statistics
        total_users = UserModel.objects.count()
        active_users = UserModel.objects.filter(account_status='active').count()
        
        # Financial statistics
        total_deposited = Balance.objects.aggregate(Sum('total_deposited'))['total_deposited__sum'] or 0
        total_withdrawn = Balance.objects.aggregate(Sum('total_withdrawn'))['total_withdrawn__sum'] or 0
        total_profit = Balance.objects.aggregate(Sum('total_profit'))['total_profit__sum'] or 0
        total_fees = Balance.objects.aggregate(Sum('total_fees'))['total_fees__sum'] or 0
        aum = Balance.objects.aggregate(Sum('current_balance'))['current_balance__sum'] or 0
        
        # Transaction statistics
        pending_withdrawals = Withdrawal.objects.filter(status='pending').count()
        pending_kyc = UserModel.objects.filter(kyc_status='pending').count()
        active_investments = Investment.objects.filter(status='active').count()
        
        stats = {
            'total_users': total_users,
            'active_users': active_users,
            'total_deposited': total_deposited,
            'total_withdrawn': total_withdrawn,
            'total_profit': total_profit,
            'total_fees': total_fees,
            'assets_under_management': aum,
            'pending_withdrawals': pending_withdrawals,
            'pending_kyc': pending_kyc,
            'active_investments': active_investments,
        }
        
        serializer = DashboardStatsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent_activity(self, request):
        """Get recent admin activity logs"""
        logs = AdminLog.objects.all()[:20]
        serializer = AdminLogSerializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def system_health(self, request):
        """Get system health status"""
        config = SystemConfiguration.get_config()
        return Response({
            'status': 'healthy',
            'timestamp': timezone.now(),
            'deposits_enabled': config.deposits_enabled,
            'withdrawals_enabled': config.withdrawals_enabled,
            'bot_trading_enabled': config.bot_trading_enabled,
            'mpesa_connected': config.mpesa_enabled,
            'crypto_connected': config.crypto_enabled,
            'email_service': config.email_notifications_enabled,
            'sms_service': config.sms_notifications_enabled,
        })


class UserManagementViewSet(viewsets.ViewSet):
    """Manage user accounts and status"""
    permission_classes = [IsAdmin]
    
    @action(detail=False, methods=['get'])
    def list_users(self, request):
        """List all users with their balances"""
        users = UserModel.objects.all()
        serializer = UserManagementSerializer(users, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def user_detail(self, request, pk=None):
        """Get detailed user information"""
        try:
            user = UserModel.objects.get(user_id=pk)
            serializer = UserManagementSerializer(user)
            return Response(serializer.data)
        except UserModel.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def suspend_user(self, request):
        """Suspend user account"""
        user_id = request.data.get('user_id')
        reason = request.data.get('reason', 'Admin action')
        
        try:
            user = UserModel.objects.get(user_id=user_id)
            user.account_status = 'suspended'
            user.save()
            
            # Log action
            admin = request.user.admin_profile
            AdminLog.objects.create(
                admin=admin,
                action_type='suspend_user',
                affected_user=user,
                reason=reason,
                ip_address=self._get_client_ip(request),
                new_value={'status': 'suspended'}
            )
            
            return Response({'message': f'User {user_id} suspended successfully'})
        except UserModel.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def activate_user(self, request):
        """Activate suspended user account"""
        user_id = request.data.get('user_id')
        reason = request.data.get('reason', 'Admin action')
        
        try:
            user = UserModel.objects.get(user_id=user_id)
            user.account_status = 'active'
            user.save()
            
            # Log action
            admin = request.user.admin_profile
            AdminLog.objects.create(
                admin=admin,
                action_type='activate_user',
                affected_user=user,
                reason=reason,
                ip_address=self._get_client_ip(request),
                new_value={'status': 'active'}
            )
            
            return Response({'message': f'User {user_id} activated successfully'})
        except UserModel.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def user_transactions(self, request):
        """Get user transaction history"""
        user_id = request.query_params.get('user_id')
        
        try:
            user = UserModel.objects.get(user_id=user_id)
            transactions = Transaction.objects.filter(user=user).order_by('-created_at')[:100]
            
            data = [{
                'id': t.id,
                'type': t.transaction_type,
                'status': t.status,
                'amount': str(t.amount),
                'receipt_id': t.receipt_id,
                'created_at': t.created_at
            } for t in transactions]
            
            return Response(data)
        except UserModel.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @staticmethod
    def _get_client_ip(request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class WithdrawalManagementViewSet(viewsets.ViewSet):
    """Manage withdrawal requests"""
    permission_classes = [IsAdmin]
    
    @action(detail=False, methods=['get'])
    def pending_withdrawals(self, request):
        """Get all pending withdrawals"""
        withdrawals = Withdrawal.objects.filter(status='pending').order_by('-created_at')
        serializer = PendingWithdrawalSerializer(withdrawals, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def approve_withdrawal(self, request):
        """Approve withdrawal request"""
        withdrawal_id = request.data.get('withdrawal_id')
        
        try:
            withdrawal = Withdrawal.objects.get(id=withdrawal_id)
            withdrawal.status = 'completed'
            withdrawal.save()
            
            # Update linked transaction
            if withdrawal.transaction:
                withdrawal.transaction.status = 'completed'
                withdrawal.transaction.save()
            
            # Log action
            admin = request.user.admin_profile
            AdminLog.objects.create(
                admin=admin,
                action_type='approve_withdrawal',
                affected_user=withdrawal.user,
                resource_type='withdrawal',
                resource_id=withdrawal_id,
                reason=request.data.get('reason', 'Approved by admin'),
                new_value={'status': 'completed'}
            )
            
            return Response({'message': f'Withdrawal {withdrawal_id} approved'})
        except Withdrawal.DoesNotExist:
            return Response({'error': 'Withdrawal not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def reject_withdrawal(self, request):
        """Reject withdrawal request"""
        withdrawal_id = request.data.get('withdrawal_id')
        reason = request.data.get('reason', 'Rejected by admin')
        
        try:
            withdrawal = Withdrawal.objects.get(id=withdrawal_id)
            withdrawal.status = 'rejected'
            withdrawal.rejection_reason = reason
            withdrawal.save()
            
            # Update linked transaction
            if withdrawal.transaction:
                withdrawal.transaction.status = 'failed'
                withdrawal.transaction.save()
            
            # Restore balance
            balance = Balance.objects.get(user=withdrawal.user)
            balance.current_balance += withdrawal.amount
            balance.save()
            
            # Log action
            admin = request.user.admin_profile
            AdminLog.objects.create(
                admin=admin,
                action_type='reject_withdrawal',
                affected_user=withdrawal.user,
                resource_type='withdrawal',
                resource_id=withdrawal_id,
                reason=reason,
                new_value={'status': 'rejected'}
            )
            
            return Response({'message': f'Withdrawal {withdrawal_id} rejected'})
        except Withdrawal.DoesNotExist:
            return Response({'error': 'Withdrawal not found'}, status=status.HTTP_404_NOT_FOUND)


class SystemConfigurationViewSet(viewsets.ViewSet):
    """Manage system configuration"""
    permission_classes = [IsAdmin]
    
    @action(detail=False, methods=['get'])
    def get_config(self, request):
        """Get current system configuration"""
        config = SystemConfiguration.get_config()
        serializer = SystemConfigurationSerializer(config)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def update_config(self, request):
        """Update system configuration"""
        admin = request.user.admin_profile
        if not admin.can_manage_admins:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        config = SystemConfiguration.get_config()
        serializer = SystemConfigurationSerializer(config, data=request.data, partial=True)
        
        if serializer.is_valid():
            config = serializer.save(last_updated_by=admin)
            
            # Log configuration change
            AdminLog.objects.create(
                admin=admin,
                action_type='system_config',
                reason='System configuration updated',
                new_value=serializer.data
            )
            
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReportingViewSet(viewsets.ViewSet):
    """Generate and export reports"""
    permission_classes = [IsAdmin]
    
    @action(detail=False, methods=['get'])
    def daily_report(self, request):
        """Get daily statistics report"""
        date = request.query_params.get('date', timezone.now().date())
        
        stats = PlatformStatistics.objects.filter(date=date).first()
        if not stats:
            return Response({'error': 'No data for this date'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PlatformStatisticsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def export_users_csv(self, request):
        """Export user list as CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="users_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['User ID', 'Username', 'Email', 'Status', 'Balance', 'Total Deposited', 'Total Profit', 'Investments'])
        
        users = UserModel.objects.all()
        for user in users:
            try:
                balance = Balance.objects.get(user=user)
                investments = Investment.objects.filter(user=user, status='active').count()
                writer.writerow([
                    user.user_id,
                    user.username,
                    user.email,
                    user.account_status,
                    balance.current_balance,
                    balance.total_deposited,
                    balance.total_profit,
                    investments
                ])
            except Balance.DoesNotExist:
                pass
        
        return response
    
    @action(detail=False, methods=['get'])
    def export_transactions_csv(self, request):
        """Export transaction report as CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="transactions_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Transaction ID', 'User ID', 'Type', 'Amount', 'Status', 'Receipt ID', 'Date'])
        
        transactions = Transaction.objects.all().order_by('-created_at')[:10000]
        for tx in transactions:
            writer.writerow([
                tx.id,
                tx.user.user_id,
                tx.transaction_type,
                tx.amount,
                tx.status,
                tx.receipt_id,
                tx.created_at
            ])
        
        return response
