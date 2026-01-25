"""
Reporting Service and API
Generates daily/monthly reports, profit statements, fee breakdowns, and analytics
"""

from rest_framework import status, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.http import HttpResponse
from datetime import datetime, timedelta, date
import csv
import json
from decimal import Decimal

from apps.payments.models import Transaction, Balance, Deposit, Withdrawal
from apps.users.models import User
from apps.admin_panel.models import PlatformStatistics
import logging

logger = logging.getLogger(__name__)


class ReportingViewSet(viewsets.ViewSet):
    """Comprehensive reporting endpoint"""
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def daily_summary(self, request):
        """
        Get daily summary report
        GET /api/reports/daily-summary/?date=2024-01-15
        """
        date_str = request.query_params.get('date')
        
        try:
            if date_str:
                report_date = datetime.fromisoformat(date_str).date()
            else:
                report_date = timezone.now().date()
            
            # Fetch or create platform statistics
            stats = PlatformStatistics.objects.filter(date=report_date).first()
            
            if not stats:
                stats = self._calculate_daily_stats(report_date)
            
            return Response({
                'success': True,
                'date': report_date.isoformat(),
                'statistics': {
                    'total_users': stats.total_users,
                    'active_users': stats.active_users,
                    'suspended_users': stats.suspended_users,
                    'total_deposited': str(stats.total_deposited),
                    'total_withdrawn': str(stats.total_withdrawn),
                    'total_profit_generated': str(stats.total_profit_generated),
                    'total_fees_collected': str(stats.total_fees_collected),
                    'assets_under_management': str(stats.assets_under_management),
                    'total_transactions': stats.total_transactions,
                    'new_deposits': stats.new_deposits,
                    'new_withdrawals': stats.new_withdrawals,
                    'kyc_verified': stats.kyc_verified,
                    'kyc_pending': stats.kyc_pending,
                    'kyc_rejected': stats.kyc_rejected,
                }
            })
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def monthly_summary(self, request):
        """
        Get monthly summary report
        GET /api/reports/monthly-summary/?month=2024-01
        """
        month_str = request.query_params.get('month')
        
        try:
            if month_str:
                year, month = map(int, month_str.split('-'))
                if month == 12:
                    start_date = date(year, month, 1)
                    end_date = date(year + 1, 1, 1)
                else:
                    start_date = date(year, month, 1)
                    end_date = date(year, month + 1, 1)
            else:
                today = date.today()
                start_date = date(today.year, today.month, 1)
                if today.month == 12:
                    end_date = date(today.year + 1, 1, 1)
                else:
                    end_date = date(today.year, today.month + 1, 1)
            
            stats = self._calculate_period_stats(start_date, end_date)
            
            return Response({
                'success': True,
                'period': f'{start_date.isoformat()} to {end_date.isoformat()}',
                'statistics': stats
            })
        except ValueError:
            return Response(
                {'error': 'Invalid month format. Use YYYY-MM'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def user_profit_statement(self, request):
        """
        Get detailed profit statement for a user
        GET /api/reports/user-profit-statement/?user_id=KE-QC-00001&start_date=2024-01-01&end_date=2024-01-31
        """
        user_id = request.query_params.get('user_id')
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(user_id=user_id)
            balance = Balance.objects.get(user=user)
            
            if start_date_str:
                start_date = datetime.fromisoformat(start_date_str)
            else:
                start_date = timezone.now().replace(day=1)
            
            if end_date_str:
                end_date = datetime.fromisoformat(end_date_str)
            else:
                end_date = timezone.now()
            
            # Get transactions for period
            deposits = Transaction.objects.filter(
                user=user, transaction_type='deposit', status='completed',
                created_at__range=[start_date, end_date]
            ).aggregate(total=Sum('amount'))['total'] or Decimal(0)
            
            withdrawals = Transaction.objects.filter(
                user=user, transaction_type='withdrawal', status='completed',
                created_at__range=[start_date, end_date]
            ).aggregate(total=Sum('amount'))['total'] or Decimal(0)
            
            profits = Transaction.objects.filter(
                user=user, transaction_type='profit', status='completed',
                created_at__range=[start_date, end_date]
            ).aggregate(total=Sum('amount'))['total'] or Decimal(0)
            
            fees = Transaction.objects.filter(
                user=user, transaction_type='fee', status='completed',
                created_at__range=[start_date, end_date]
            ).aggregate(total=Sum('amount'))['total'] or Decimal(0)
            
            net_profit = profits - fees
            
            return Response({
                'success': True,
                'user_id': user.user_id,
                'email': user.email,
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'lifetime': {
                    'total_deposited': str(balance.total_deposited),
                    'total_withdrawn': str(balance.total_withdrawn),
                    'total_profit': str(balance.total_profit),
                    'total_fees': str(balance.total_fees),
                    'current_balance': str(balance.current_balance)
                },
                'period_details': {
                    'deposits': str(deposits),
                    'withdrawals': str(withdrawals),
                    'profits': str(profits),
                    'fees': str(fees),
                    'net_profit': str(net_profit)
                },
                'currency': 'KES'
            })
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DDTHH:MM:SS'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def fee_breakdown(self, request):
        """
        Get platform fee breakdown and analysis
        GET /api/reports/fee-breakdown/?start_date=2024-01-01&end_date=2024-01-31&group_by=user
        """
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        group_by = request.query_params.get('group_by', 'day')  # day, user, transaction_type
        
        try:
            if start_date_str:
                start_date = datetime.fromisoformat(start_date_str)
            else:
                start_date = timezone.now() - timedelta(days=30)
            
            if end_date_str:
                end_date = datetime.fromisoformat(end_date_str)
            else:
                end_date = timezone.now()
            
            fees = Transaction.objects.filter(
                transaction_type='fee', status='completed',
                created_at__range=[start_date, end_date]
            )
            
            total_fees = fees.aggregate(Sum('amount'))['amount__sum'] or Decimal(0)
            fee_count = fees.count()
            
            # Group breakdown
            if group_by == 'user':
                breakdown = fees.values('user__user_id', 'user__email').annotate(
                    total=Sum('amount'),
                    count=Count('id')
                ).order_by('-total')[:20]
                
                breakdown_data = [{
                    'user_id': item['user__user_id'],
                    'email': item['user__email'],
                    'total_fees': str(item['total']),
                    'transaction_count': item['count']
                } for item in breakdown]
            
            elif group_by == 'transaction_type':
                # Link to profit transactions that generated fees
                profits = Transaction.objects.filter(
                    transaction_type='profit', status='completed',
                    created_at__range=[start_date, end_date]
                )
                
                total_profits = profits.aggregate(Sum('amount'))['amount__sum'] or Decimal(0)
                fee_rate = (total_fees / total_profits * 100) if total_profits > 0 else 0
                
                breakdown_data = {
                    'total_profits': str(total_profits),
                    'total_fees': str(total_fees),
                    'effective_fee_rate': f'{fee_rate:.2f}%',
                    'expected_fee_rate': '10.00%'
                }
            
            else:  # group_by == 'day'
                daily_fees = {}
                for fee in fees:
                    day = fee.created_at.date()
                    if day not in daily_fees:
                        daily_fees[day] = Decimal(0)
                    daily_fees[day] += fee.amount
                
                breakdown_data = [{
                    'date': date_key.isoformat(),
                    'total_fees': str(amount)
                } for date_key, amount in sorted(daily_fees.items())]
            
            return Response({
                'success': True,
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'summary': {
                    'total_fees_collected': str(total_fees),
                    'fee_transactions': fee_count,
                    'average_fee': str(total_fees / max(fee_count, 1)) if fee_count > 0 else '0.00'
                },
                'breakdown': breakdown_data,
                'currency': 'KES'
            })
        except ValueError:
            return Response(
                {'error': 'Invalid date format'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def export_daily_report(self, request):
        """
        Export daily report as CSV
        GET /api/reports/export-daily/?date=2024-01-15
        """
        date_str = request.query_params.get('date')
        
        try:
            if date_str:
                report_date = datetime.fromisoformat(date_str).date()
            else:
                report_date = timezone.now().date()
            
            stats = self._calculate_daily_stats(report_date)
            
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="daily_report_{report_date}.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['Daily Platform Report', report_date])
            writer.writerow([])
            
            writer.writerow(['Metric', 'Value'])
            writer.writerow(['Total Users', stats.total_users])
            writer.writerow(['Active Users', stats.active_users])
            writer.writerow(['Suspended Users', stats.suspended_users])
            writer.writerow(['Total Deposited', stats.total_deposited])
            writer.writerow(['Total Withdrawn', stats.total_withdrawn])
            writer.writerow(['Total Profit Generated', stats.total_profit_generated])
            writer.writerow(['Platform Fees (10%)', stats.total_fees_collected])
            writer.writerow(['Assets Under Management', stats.assets_under_management])
            writer.writerow(['Total Transactions', stats.total_transactions])
            writer.writerow(['New Deposits', stats.new_deposits])
            writer.writerow(['New Withdrawals', stats.new_withdrawals])
            writer.writerow(['KYC Verified', stats.kyc_verified])
            writer.writerow(['KYC Pending', stats.kyc_pending])
            writer.writerow(['KYC Rejected', stats.kyc_rejected])
            
            return response
        except ValueError:
            return Response(
                {'error': 'Invalid date format'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def export_user_statement(self, request):
        """
        Export user profit statement as CSV
        GET /api/reports/export-statement/?user_id=KE-QC-00001&start_date=2024-01-01&end_date=2024-01-31
        """
        user_id = request.query_params.get('user_id')
        start_date_str = request.query_params.get('start_date', timezone.now().replace(day=1).isoformat())
        end_date_str = request.query_params.get('end_date', timezone.now().isoformat())
        
        try:
            user = User.objects.get(user_id=user_id)
            start_date = datetime.fromisoformat(start_date_str)
            end_date = datetime.fromisoformat(end_date_str)
            
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="statement_{user_id}_{start_date.date()}_to_{end_date.date()}.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['Profit Statement', user_id, user.email])
            writer.writerow(['Period', f'{start_date.date()} to {end_date.date()}'])
            writer.writerow([])
            
            # Get transactions
            deposits = Transaction.objects.filter(
                user=user, transaction_type='deposit', status='completed',
                created_at__range=[start_date, end_date]
            )
            withdrawals = Transaction.objects.filter(
                user=user, transaction_type='withdrawal', status='completed',
                created_at__range=[start_date, end_date]
            )
            profits = Transaction.objects.filter(
                user=user, transaction_type='profit', status='completed',
                created_at__range=[start_date, end_date]
            )
            fees = Transaction.objects.filter(
                user=user, transaction_type='fee', status='completed',
                created_at__range=[start_date, end_date]
            )
            
            total_deposits = deposits.aggregate(Sum('amount'))['amount__sum'] or 0
            total_withdrawals = withdrawals.aggregate(Sum('amount'))['amount__sum'] or 0
            total_profits = profits.aggregate(Sum('amount'))['amount__sum'] or 0
            total_fees = fees.aggregate(Sum('amount'))['amount__sum'] or 0
            
            writer.writerow(['Category', 'Amount (KES)'])
            writer.writerow(['Deposits', total_deposits])
            writer.writerow(['Withdrawals', total_withdrawals])
            writer.writerow(['Profits', total_profits])
            writer.writerow(['Fees Deducted', total_fees])
            writer.writerow(['Net Profit', total_profits - total_fees])
            
            return response
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError:
            return Response(
                {'error': 'Invalid date format'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Helper methods
    
    @staticmethod
    def _calculate_daily_stats(report_date):
        """Calculate statistics for a specific date"""
        start = datetime.combine(report_date, datetime.min.time())
        end = datetime.combine(report_date, datetime.max.time())
        
        # User statistics
        total_users = User.objects.count()
        active_users = User.objects.filter(account_status='active').count()
        suspended_users = User.objects.filter(account_status='suspended').count()
        
        # Financial statistics
        total_deposited = Transaction.objects.filter(
            transaction_type='deposit', status='completed'
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal(0)
        
        total_withdrawn = Transaction.objects.filter(
            transaction_type='withdrawal', status='completed'
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal(0)
        
        total_profit = Transaction.objects.filter(
            transaction_type='profit', status='completed'
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal(0)
        
        total_fees = Transaction.objects.filter(
            transaction_type='fee', status='completed'
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal(0)
        
        aum = total_deposited - total_withdrawn + total_profit
        
        # Daily transactions
        new_deposits = Deposit.objects.filter(
            created_at__range=[start, end], status='confirmed'
        ).count()
        
        new_withdrawals = Withdrawal.objects.filter(
            created_at__range=[start, end], status='completed'
        ).count()
        
        total_transactions = Transaction.objects.filter(
            created_at__range=[start, end]
        ).count()
        
        # KYC statistics
        kyc_verified = User.objects.filter(kyc_status='verified').count()
        kyc_pending = User.objects.filter(kyc_status='pending').count()
        kyc_rejected = User.objects.filter(kyc_status='rejected').count()
        
        # Create or update statistics record
        stats, created = PlatformStatistics.objects.get_or_create(date=report_date)
        stats.total_users = total_users
        stats.active_users = active_users
        stats.suspended_users = suspended_users
        stats.total_deposited = total_deposited
        stats.total_withdrawn = total_withdrawn
        stats.total_profit_generated = total_profit
        stats.total_fees_collected = total_fees
        stats.assets_under_management = aum
        stats.total_transactions = total_transactions
        stats.new_deposits = new_deposits
        stats.new_withdrawals = new_withdrawals
        stats.kyc_verified = kyc_verified
        stats.kyc_pending = kyc_pending
        stats.kyc_rejected = kyc_rejected
        stats.save()
        
        return stats
    
    @staticmethod
    def _calculate_period_stats(start_date, end_date):
        """Calculate statistics for a period"""
        # Financial statistics
        total_deposited = Transaction.objects.filter(
            transaction_type='deposit', status='completed',
            created_at__gte=start_date, created_at__lt=end_date
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal(0)
        
        total_withdrawn = Transaction.objects.filter(
            transaction_type='withdrawal', status='completed',
            created_at__gte=start_date, created_at__lt=end_date
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal(0)
        
        total_profit = Transaction.objects.filter(
            transaction_type='profit', status='completed',
            created_at__gte=start_date, created_at__lt=end_date
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal(0)
        
        total_fees = Transaction.objects.filter(
            transaction_type='fee', status='completed',
            created_at__gte=start_date, created_at__lt=end_date
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal(0)
        
        new_users = User.objects.filter(
            created_at__gte=start_date, created_at__lt=end_date
        ).count()
        
        return {
            'total_deposited': str(total_deposited),
            'total_withdrawn': str(total_withdrawn),
            'total_profits': str(total_profit),
            'total_fees': str(total_fees),
            'net_platform_revenue': str(total_fees),
            'new_users_count': new_users,
            'assets_under_management': str(total_deposited - total_withdrawn + total_profit),
            'currency': 'KES'
        }
