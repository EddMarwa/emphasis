"""
Additional admin panel views for comprehensive user management and reporting
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
import csv
import json

from apps.users.models import User, LoginHistory, FailedLoginAttempt
from apps.payments.models import Balance, Transaction
from apps.admin_panel.models import AdminUser, AdminLog, PlatformStatistics
from apps.referrals.models import Referral, ReferralBonus


def is_admin_user(user):
    """Check if user is an admin"""
    try:
        return AdminUser.objects.filter(user=user, is_active=True).exists()
    except:
        return False


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def edit_user(request):
    """Edit user account details (admin only)"""
    if not is_admin_user(request.user):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    user_id = request.data.get('user_id')
    
    try:
        user = User.objects.get(user_id=user_id)
        admin = request.user.admin_profile
        old_values = {
            'email': user.email,
            'phone': user.phone,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'account_status': user.account_status,
            'kyc_status': user.kyc_status,
        }
        
        # Update allowed fields
        if 'email' in request.data:
            user.email = request.data['email']
        if 'phone' in request.data:
            user.phone = request.data['phone']
        if 'first_name' in request.data:
            user.first_name = request.data['first_name']
        if 'last_name' in request.data:
            user.last_name = request.data['last_name']
        if 'account_status' in request.data:
            user.account_status = request.data['account_status']
        if 'kyc_status' in request.data:
            user.kyc_status = request.data['kyc_status']
        
        user.save()
        
        # Log the change
        AdminLog.objects.create(
            admin=admin,
            action_type='create_user',  # Using existing action type
            affected_user=user,
            old_value=old_values,
            new_value={
                'email': user.email,
                'phone': user.phone,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'account_status': user.account_status,
                'kyc_status': user.kyc_status,
            },
            reason=request.data.get('reason', 'User details updated by admin'),
            ip_address=get_client_ip(request)
        )
        
        return Response({
            'message': 'User updated successfully',
            'user_id': user.user_id,
            'email': user.email,
            'phone': user.phone,
            'account_status': user.account_status
        })
        
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_activity_logs(request):
    """Get detailed user activity logs (admin only)"""
    if not is_admin_user(request.user):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    user_id = request.query_params.get('user_id')
    days = int(request.query_params.get('days', 30))
    
    try:
        user = User.objects.get(user_id=user_id)
        start_date = timezone.now() - timedelta(days=days)
        
        # Get login history
        logins = LoginHistory.objects.filter(
            user=user,
            login_time__gte=start_date
        ).order_by('-login_time')[:50]
        
        login_data = [{
            'timestamp': login.login_time.isoformat(),
            'ip_address': login.ip_address,
            'success': login.success,
            'device_info': login.device_info,
            'user_agent': login.user_agent[:100] if login.user_agent else ''
        } for login in logins]
        
        # Get failed attempts
        failed_attempts = FailedLoginAttempt.objects.filter(
            email_or_user_id__in=[user.email, user.user_id],
            attempt_time__gte=start_date
        ).order_by('-attempt_time')[:50]
        
        failed_data = [{
            'timestamp': attempt.attempt_time.isoformat(),
            'ip_address': attempt.ip_address,
            'reason': attempt.reason
        } for attempt in failed_attempts]
        
        # Get transactions
        transactions = Transaction.objects.filter(
            user=user,
            created_at__gte=start_date
        ).order_by('-created_at')[:50]
        
        transaction_data = [{
            'timestamp': tx.created_at.isoformat(),
            'type': tx.transaction_type,
            'amount': str(tx.amount),
            'status': tx.status,
            'reference': tx.transaction_reference
        } for tx in transactions]
        
        return Response({
            'user_id': user_id,
            'login_history': login_data,
            'failed_attempts': failed_data,
            'recent_transactions': transaction_data,
            'total_logins': len(login_data),
            'total_failed_attempts': len(failed_data)
        })
        
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_users_excel(request):
    """Export users list to CSV (Excel compatible)"""
    if not is_admin_user(request.user):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # Create the HttpResponse object with CSV header
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="users_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        # Write header
        writer.writerow([
            'User ID', 'Email', 'Phone', 'Full Name', 'Country', 'Account Status',
            'KYC Status', 'Current Balance', 'Total Deposited', 'Total Withdrawn',
            'Total Profit', 'Registration Date'
        ])
        
        # Write data
        users = User.objects.all().select_related()
        for user in users:
            try:
                balance = Balance.objects.get(user=user)
                current_balance = balance.current_balance
                total_deposited = balance.total_deposited
                total_withdrawn = balance.total_withdrawn
                total_profit = balance.total_profit
            except Balance.DoesNotExist:
                current_balance = total_deposited = total_withdrawn = total_profit = 0
            
            writer.writerow([
                user.user_id,
                user.email,
                user.phone,
                f"{user.first_name} {user.last_name}",
                user.country_code,
                user.account_status,
                user.kyc_status,
                float(current_balance),
                float(total_deposited),
                float(total_withdrawn),
                float(total_profit),
                user.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        # Log export action
        admin = request.user.admin_profile
        AdminLog.objects.create(
            admin=admin,
            action_type='export_report',
            reason='Users export to CSV',
            ip_address=get_client_ip(request)
        )
        
        return response
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_transactions_excel(request):
    """Export transactions to CSV"""
    if not is_admin_user(request.user):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="transactions_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Transaction ID', 'User ID', 'Type', 'Amount', 'Status',
            'Payment Method', 'Reference', 'Created At', 'Completed At'
        ])
        
        transactions = Transaction.objects.filter(
            created_at__gte=start_date
        ).select_related('user').order_by('-created_at')
        
        for tx in transactions:
            writer.writerow([
                tx.id,
                tx.user.user_id if tx.user else '',
                tx.transaction_type,
                float(tx.amount),
                tx.status,
                tx.payment_method,
                tx.transaction_reference,
                tx.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                tx.updated_at.strftime('%Y-%m-%d %H:%M:%S') if tx.updated_at else ''
            ])
        
        # Log export
        admin = request.user.admin_profile
        AdminLog.objects.create(
            admin=admin,
            action_type='export_report',
            reason=f'Transactions export ({days} days)',
            ip_address=get_client_ip(request)
        )
        
        return response
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def platform_revenue_report(request):
    """Get detailed platform revenue breakdown"""
    if not is_admin_user(request.user):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        period = request.query_params.get('period', 'monthly')  # daily, weekly, monthly, yearly
        
        today = timezone.now().date()
        if period == 'daily':
            start_date = today
            end_date = today + timedelta(days=1)
        elif period == 'weekly':
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=7)
        elif period == 'monthly':
            start_date = today.replace(day=1)
            if today.month == 12:
                end_date = today.replace(year=today.year + 1, month=1, day=1)
            else:
                end_date = today.replace(month=today.month + 1, day=1)
        else:  # yearly
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(year=today.year + 1, month=1, day=1)
        
        # Calculate fees collected (10% of profits)
        total_fees = Transaction.objects.filter(
            transaction_type='fee',
            status='completed',
            created_at__gte=start_date,
            created_at__lt=end_date
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Total deposits
        total_deposits = Transaction.objects.filter(
            transaction_type='deposit',
            status='completed',
            created_at__gte=start_date,
            created_at__lt=end_date
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Total withdrawals
        total_withdrawals = Transaction.objects.filter(
            transaction_type='withdrawal',
            status='completed',
            created_at__gte=start_date,
            created_at__lt=end_date
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Total profits
        total_profits = Transaction.objects.filter(
            transaction_type='profit',
            status='completed',
            created_at__gte=start_date,
            created_at__lt=end_date
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Referral bonuses paid
        referral_bonuses_paid = ReferralBonus.objects.filter(
            status='distributed',
            distributed_at__gte=start_date,
            distributed_at__lt=end_date
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Active users count
        active_users = User.objects.filter(
            account_status='active',
            last_login__gte=start_date
        ).count()
        
        return Response({
            'period': period,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'total_revenue': float(total_fees),
            'total_deposits': float(total_deposits),
            'total_withdrawals': float(total_withdrawals),
            'total_profits_generated': float(total_profits),
            'referral_bonuses_paid': float(referral_bonuses_paid),
            'net_cash_flow': float(total_deposits - total_withdrawals),
            'active_users_count': active_users,
            'average_deposit': float(total_deposits / active_users) if active_users > 0 else 0
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_client_ip(request):
    """Extract client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
