"""
Payment Integration API Endpoints
Handles M-Pesa STK push, crypto payment verification, and payment status
"""

from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum
from datetime import datetime, timedelta
from .models import Transaction, Deposit, Withdrawal, Balance
from .services import (
    MPesaIntegration, CryptoIntegration, PaymentVerificationService, ReportingService
)
from apps.users.models import User
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def initiate_mpesa_payment(request):
    """
    Initiate M-Pesa STK Push for deposit
    
    POST /api/payments/mpesa/stk-push/
    {
        "amount": 10000,
        "phone": "254712345678"
    }
    """
    user = request.user
    amount = request.data.get('amount')
    phone = request.data.get('phone')
    
    if not amount or not phone:
        return Response(
            {'error': 'Amount and phone are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        amount = float(amount)
        if amount < 10:
            return Response(
                {'error': 'Minimum deposit is 10 KES'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        mpesa = MPesaIntegration()
        result = mpesa.stk_push(phone, amount)
        
        if result['success']:
            # Create deposit record
            deposit = Deposit.objects.create(
                user=user,
                amount=amount,
                payment_method='mpesa',
                status='pending',
                mpesa_checkout_request_id=result['checkout_request_id']
            )
            
            return Response({
                'success': True,
                'message': 'STK Push initiated successfully',
                'checkout_request_id': result['checkout_request_id'],
                'deposit_id': deposit.id,
                'amount': amount,
                'currency': 'KES'
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'error': result.get('error', 'Failed to initiate payment')},
                status=status.HTTP_400_BAD_REQUEST
            )
    except ValueError:
        return Response(
            {'error': 'Invalid amount'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"M-Pesa error: {e}")
        return Response(
            {'error': 'Payment initialization failed'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def check_mpesa_payment(request):
    """
    Check M-Pesa payment status
    
    GET /api/payments/mpesa/status/?checkout_request_id=<id>
    """
    checkout_request_id = request.query_params.get('checkout_request_id')
    
    if not checkout_request_id:
        return Response(
            {'error': 'checkout_request_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        mpesa = MPesaIntegration()
        result = mpesa.query_transaction_status(checkout_request_id)
        
        if result['success']:
            # Update deposit if confirmed
            if result['result_code'] == '0':
                try:
                    deposit = Deposit.objects.get(
                        mpesa_checkout_request_id=checkout_request_id
                    )
                    if deposit.status != 'confirmed':
                        deposit.status = 'confirmed'
                        deposit.confirmed_at = timezone.now()
                        deposit.save()
                        
                        # Update balance
                        balance = Balance.objects.get(user=deposit.user)
                        balance.total_deposited += deposit.amount
                        balance.current_balance += deposit.amount
                        balance.save()
                        
                        # Create transaction
                        Transaction.objects.create(
                            user=deposit.user,
                            transaction_type='deposit',
                            amount=deposit.amount,
                            status='completed',
                            payment_method='mpesa',
                            receipt_id=str(deposit.id),
                            reference=result.get('merchant_request_id'),
                            completed_at=timezone.now()
                        )
                except Deposit.DoesNotExist:
                    pass
            
            return Response({
                'success': True,
                'status': 'confirmed' if result['result_code'] == '0' else 'pending',
                'result_code': result['result_code'],
                'result_description': result['result_desc']
            })
        else:
            return Response(
                {'error': result.get('error')},
                status=status.HTTP_400_BAD_REQUEST
            )
    except Exception as e:
        logger.error(f"Payment status check error: {e}")
        return Response(
            {'error': 'Failed to check payment status'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_crypto_exchange_rate(request):
    """
    Get current crypto to KES exchange rate
    
    GET /api/payments/crypto/exchange-rate/?symbol=USDT
    """
    symbol = request.query_params.get('symbol', 'USDT')
    
    try:
        crypto = CryptoIntegration()
        result = crypto.get_exchange_rate(symbol, 'KES')
        
        if result['success']:
            return Response({
                'success': True,
                'symbol': symbol,
                'rate': result['rate'],
                'currency': 'KES',
                'change_24h': result['change_24h'],
                'timestamp': result['timestamp']
            })
        else:
            return Response(
                {'error': result.get('error')},
                status=status.HTTP_400_BAD_REQUEST
            )
    except Exception as e:
        logger.error(f"Exchange rate error: {e}")
        return Response(
            {'error': 'Failed to fetch exchange rate'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_crypto_wallet(request):
    """
    Generate wallet address for crypto deposit
    
    POST /api/payments/crypto/generate-address/
    {
        "crypto_symbol": "USDT"
    }
    """
    user = request.user
    crypto_symbol = request.data.get('crypto_symbol', 'USDT')
    
    try:
        crypto = CryptoIntegration()
        result = crypto.generate_wallet_address(crypto_symbol, user.user_id)
        
        if result['success']:
            return Response({
                'success': True,
                'symbol': crypto_symbol,
                'address': result['address'],
                'expires_in': result['expires_in'],
                'user_id': user.user_id
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'error': result.get('error')},
                status=status.HTTP_400_BAD_REQUEST
            )
    except Exception as e:
        logger.error(f"Wallet generation error: {e}")
        return Response(
            {'error': 'Failed to generate wallet address'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def verify_crypto_deposit(request):
    """
    Verify crypto transaction and confirm deposit
    
    POST /api/payments/crypto/verify-deposit/
    {
        "deposit_id": 1,
        "method": "usdt_erc20"
    }
    """
    deposit_id = request.data.get('deposit_id')
    method = request.data.get('method')
    
    if not deposit_id or not method:
        return Response(
            {'error': 'deposit_id and method are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        service = PaymentVerificationService()
        result = service.verify_deposit(deposit_id, method)
        
        if result['success']:
            return Response({
                'success': True,
                'message': result['message'],
                'status': result['status']
            })
        else:
            return Response(
                {'error': result.get('error', result.get('message'))},
                status=status.HTTP_400_BAD_REQUEST
            )
    except Exception as e:
        logger.error(f"Deposit verification error: {e}")
        return Response(
            {'error': 'Failed to verify deposit'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_payment_status(request):
    """
    Get status of any payment
    
    GET /api/payments/status/?transaction_id=<id>
    """
    transaction_id = request.query_params.get('transaction_id')
    
    if not transaction_id:
        return Response(
            {'error': 'transaction_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        service = PaymentVerificationService()
        result = service.get_payment_status(transaction_id)
        
        if result['success']:
            return Response(result)
        else:
            return Response(
                {'error': result.get('error')},
                status=status.HTTP_404_NOT_FOUND
            )
    except Exception as e:
        logger.error(f"Status check error: {e}")
        return Response(
            {'error': 'Failed to check status'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_transactions(request):
    """
    Get user's transaction history
    
    GET /api/payments/transactions/
    """
    user = request.user
    transaction_type = request.query_params.get('type')
    status_filter = request.query_params.get('status')
    
    transactions = Transaction.objects.filter(user=user).order_by('-created_at')
    
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    
    if status_filter:
        transactions = transactions.filter(status=status_filter)
    
    data = [{
        'id': tx.id,
        'type': tx.transaction_type,
        'amount': str(tx.amount),
        'status': tx.status,
        'payment_method': tx.payment_method,
        'reference': tx.reference,
        'created_at': tx.created_at.isoformat(),
        'completed_at': tx.completed_at.isoformat() if tx.completed_at else None,
        'description': tx.description
    } for tx in transactions[:100]]
    
    return Response({
        'success': True,
        'count': len(data),
        'transactions': data
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def generate_profit_statement(request):
    """
    Generate user profit statement for period
    
    GET /api/payments/profit-statement/?start_date=2024-01-01&end_date=2024-01-31
    """
    user = request.user
    start_date_str = request.query_params.get('start_date')
    end_date_str = request.query_params.get('end_date')
    
    try:
        if start_date_str:
            start_date = datetime.fromisoformat(start_date_str)
        else:
            start_date = timezone.now().replace(day=1)
        
        if end_date_str:
            end_date = datetime.fromisoformat(end_date_str)
        else:
            end_date = timezone.now()
        
        result = ReportingService.generate_user_profit_statement(user, start_date, end_date)
        
        return Response({
            'success': True,
            'statement': result
        })
    except ValueError:
        return Response(
            {'error': 'Invalid date format. Use YYYY-MM-DD'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Statement generation error: {e}")
        return Response(
            {'error': 'Failed to generate statement'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def platform_statistics(request):
    """
    Get platform-wide financial statistics
    
    GET /api/payments/platform-stats/
    """
    try:
        total_deposited = Transaction.objects.filter(
            transaction_type='deposit', status='completed'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        total_withdrawn = Transaction.objects.filter(
            transaction_type='withdrawal', status='completed'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        total_profit = Transaction.objects.filter(
            transaction_type='profit', status='completed'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        total_fees = Transaction.objects.filter(
            transaction_type='fee', status='completed'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        return Response({
            'success': True,
            'total_deposited': str(total_deposited),
            'total_withdrawn': str(total_withdrawn),
            'total_profit': str(total_profit),
            'platform_revenue': str(total_fees),
            'aum': str(total_deposited - total_withdrawn + total_profit),
            'currency': 'KES'
        })
    except Exception as e:
        logger.error(f"Statistics error: {e}")
        return Response(
            {'error': 'Failed to fetch statistics'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
