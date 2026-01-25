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
from apps.users.serializers import UserRegistrationSerializer
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

    @action(detail=False, methods=['post'])
    def create_user(self, request):
        """Create a new user account (admin initiated)"""
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Log action
        admin = getattr(request.user, 'admin_profile', None)
        if admin:
            AdminLog.objects.create(
                admin=admin,
                action_type='create_user',
                affected_user=user,
                reason=request.data.get('reason', 'Created by admin'),
                ip_address=self._get_client_ip(request),
                new_value={'user_id': user.user_id, 'email': user.email}
            )

        return Response(UserManagementSerializer(user).data, status=status.HTTP_201_CREATED)
    
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


class TransactionAdjustmentViewSet(viewsets.ViewSet):
    """Manage and adjust transactions with audit trail"""
    permission_classes = [IsAdmin]
    
    @action(detail=False, methods=['post'])
    def adjust_balance(self, request):
        """Manually adjust user balance with audit trail"""
        admin = request.user.admin_profile
        
        if not admin.can_adjust_transactions:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        user_id = request.data.get('user_id')
        adjustment_amount = float(request.data.get('amount', 0))
        adjustment_type = request.data.get('type')  # 'credit' or 'debit'
        reason = request.data.get('reason', 'Manual adjustment by admin')
        
        try:
            user = UserModel.objects.get(user_id=user_id)
            balance = Balance.objects.get(user=user)
            
            # Store old values for audit trail
            old_balance = balance.current_balance
            
            # Adjust balance
            if adjustment_type == 'credit':
                balance.current_balance += adjustment_amount
                transaction_type = 'admin_credit'
                new_value = {
                    'adjustment_type': 'credit',
                    'amount': adjustment_amount,
                    'old_balance': str(old_balance),
                    'new_balance': str(balance.current_balance)
                }
            elif adjustment_type == 'debit':
                balance.current_balance -= adjustment_amount
                transaction_type = 'admin_debit'
                new_value = {
                    'adjustment_type': 'debit',
                    'amount': adjustment_amount,
                    'old_balance': str(old_balance),
                    'new_balance': str(balance.current_balance)
                }
            else:
                return Response(
                    {'error': 'Invalid adjustment type. Use "credit" or "debit"'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            balance.save()
            
            # Create transaction record
            from apps.payments.models import Transaction as TxModel
            tx = TxModel.objects.create(
                user=user,
                transaction_type=transaction_type,
                amount=adjustment_amount,
                status='completed',
                receipt_id=f'ADJ-{admin.id}-{int(timezone.now().timestamp())}',
                description=reason
            )
            
            # Log the action
            AdminLog.objects.create(
                admin=admin,
                action_type='adjust_balance',
                affected_user=user,
                resource_type='balance',
                resource_id=balance.id,
                old_value={'balance': str(old_balance)},
                new_value=new_value,
                reason=reason,
                ip_address=self._get_client_ip(request),
            )
            
            return Response({
                'message': f'Balance adjusted successfully for {user_id}',
                'user_id': user_id,
                'adjustment_amount': str(adjustment_amount),
                'adjustment_type': adjustment_type,
                'old_balance': str(old_balance),
                'new_balance': str(balance.current_balance),
                'transaction_id': tx.id
            })
        except UserModel.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Balance.DoesNotExist:
            return Response({'error': 'User balance not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def reverse_transaction(self, request):
        """Reverse a completed transaction"""
        admin = request.user.admin_profile
        
        if not admin.can_adjust_transactions:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        transaction_id = request.data.get('transaction_id')
        reason = request.data.get('reason', 'Transaction reversal')
        
        try:
            from apps.payments.models import Transaction as TxModel
            tx = TxModel.objects.get(id=transaction_id)
            
            if tx.status != 'completed':
                return Response(
                    {'error': 'Only completed transactions can be reversed'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Store old value
            old_status = tx.status
            
            # Reverse the transaction
            tx.status = 'reversed'
            tx.save()
            
            # Adjust user balance
            balance = Balance.objects.get(user=tx.user)
            
            if tx.transaction_type == 'deposit':
                balance.total_deposited -= tx.amount
                balance.current_balance -= tx.amount
            elif tx.transaction_type == 'withdrawal':
                balance.total_withdrawn -= tx.amount
                balance.current_balance += tx.amount
            elif tx.transaction_type == 'profit':
                balance.total_profit -= tx.amount
                balance.current_balance -= tx.amount
            elif tx.transaction_type == 'fee':
                balance.total_fees -= tx.amount
                balance.current_balance += tx.amount
            
            balance.save()
            
            # Log the action
            AdminLog.objects.create(
                admin=admin,
                action_type='adjust_transaction',
                affected_user=tx.user,
                resource_type='transaction',
                resource_id=transaction_id,
                old_value={'status': old_status},
                new_value={'status': 'reversed'},
                reason=reason,
                ip_address=self._get_client_ip(request),
            )
            
            return Response({
                'message': f'Transaction {transaction_id} reversed successfully',
                'transaction_id': transaction_id,
                'user_id': tx.user.user_id,
                'original_amount': str(tx.amount),
                'new_user_balance': str(balance.current_balance)
            })
        except TxModel.DoesNotExist:
            return Response({'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def audit_trail(self, request):
        """Get audit trail for admin actions"""
        user_id = request.query_params.get('user_id')
        action_type = request.query_params.get('action_type')
        
        logs = AdminLog.objects.all().order_by('-created_at')
        
        if user_id:
            try:
                user = UserModel.objects.get(user_id=user_id)
                logs = logs.filter(affected_user=user)
            except UserModel.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if action_type:
            logs = logs.filter(action_type=action_type)
        
        serializer = AdminLogSerializer(logs[:500], many=True)
        return Response(serializer.data)
    
    @staticmethod
    def _get_client_ip(request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


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
    
    @action(detail=False, methods=['get'])
    def user_profit_statements(self, request):
        """Get user profit statements"""
        user_id = request.query_params.get('user_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        try:
            user = UserModel.objects.get(user_id=user_id)
            balance = Balance.objects.get(user=user)
            
            # Get profit transactions
            profits = Transaction.objects.filter(
                user=user, transaction_type='profit', status='completed'
            )
            
            # Get fees deducted
            fees = Transaction.objects.filter(
                user=user, transaction_type='fee', status='completed'
            )
            
            if start_date:
                profits = profits.filter(created_at__gte=start_date)
                fees = fees.filter(created_at__gte=start_date)
            
            if end_date:
                profits = profits.filter(created_at__lte=end_date)
                fees = fees.filter(created_at__lte=end_date)
            
            total_profits = profits.aggregate(Sum('amount'))['amount__sum'] or 0
            total_fees = fees.aggregate(Sum('amount'))['amount__sum'] or 0
            
            return Response({
                'user_id': user.user_id,
                'total_deposited': str(balance.total_deposited),
                'total_withdrawn': str(balance.total_withdrawn),
                'total_profit': str(balance.total_profit),
                'total_fees': str(balance.total_fees),
                'current_balance': str(balance.current_balance),
                'period_profit': str(total_profits),
                'period_fees': str(total_fees),
                'net_profit': str(total_profits - total_fees),
            })
        except (UserModel.DoesNotExist, Balance.DoesNotExist):
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def platform_fee_report(self, request):
        """Get platform fee calculations and breakdown"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        fees = Transaction.objects.filter(transaction_type='fee', status='completed')
        
        if start_date:
            fees = fees.filter(created_at__gte=start_date)
        
        if end_date:
            fees = fees.filter(created_at__lte=end_date)
        
        total_fees = fees.aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Fee breakdown by user
        fee_breakdown = fees.values('user__user_id', 'user__email').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')
        
        return Response({
            'total_fees_collected': str(total_fees),
            'fee_count': fees.count(),
            'average_fee': str(total_fees / max(fees.count(), 1)),
            'breakdown': [
                {
                    'user_id': item['user__user_id'],
                    'email': item['user__email'],
                    'total_fees': str(item['total']),
                    'fee_transactions': item['count']
                }
                for item in fee_breakdown
            ]
        })
    
    @action(detail=False, methods=['get'])
    def monthly_summary(self, request):
        """Get monthly summary statistics"""
        month = request.query_params.get('month')  # Format: YYYY-MM
        
        if month:
            year, month_num = map(int, month.split('-'))
            from datetime import date
            if month_num == 12:
                start_date = date(year, month_num, 1)
                end_date = date(year + 1, 1, 1)
            else:
                start_date = date(year, month_num, 1)
                end_date = date(year, month_num + 1, 1)
        else:
            from datetime import date
            today = date.today()
            start_date = date(today.year, today.month, 1)
            if today.month == 12:
                end_date = date(today.year + 1, 1, 1)
            else:
                end_date = date(today.year, today.month + 1, 1)
        
        # Deposits
        deposits = Transaction.objects.filter(
            transaction_type='deposit', status='completed',
            created_at__gte=start_date, created_at__lt=end_date
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Withdrawals
        withdrawals = Transaction.objects.filter(
            transaction_type='withdrawal', status='completed',
            created_at__gte=start_date, created_at__lt=end_date
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Profits
        profits = Transaction.objects.filter(
            transaction_type='profit', status='completed',
            created_at__gte=start_date, created_at__lt=end_date
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Fees
        fees = Transaction.objects.filter(
            transaction_type='fee', status='completed',
            created_at__gte=start_date, created_at__lt=end_date
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # New users
        new_users = UserModel.objects.filter(
            created_at__gte=start_date, created_at__lt=end_date
        ).count()
        
        return Response({
            'period': f'{start_date} to {end_date}',
            'total_deposits': str(deposits),
            'total_withdrawals': str(withdrawals),
            'total_profits': str(profits),
            'total_fees': str(fees),
            'net_platform_revenue': str(fees),
            'new_users_count': new_users,
            'assets_under_management': str(deposits - withdrawals + profits),
        })
