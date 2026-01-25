"""
Payment Integration Service
Handles M-Pesa and Crypto payment processing, verification, and status tracking
"""

import requests
import json
from datetime import datetime, timedelta
from decimal import Decimal
import logging
from django.conf import settings
from django.utils import timezone
from .models import Transaction, Deposit, Withdrawal, Balance
from apps.users.models import User

logger = logging.getLogger(__name__)


class MPesaIntegration:
    """M-Pesa Daraja API integration"""
    
    def __init__(self):
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.shortcode = settings.MPESA_SHORTCODE
        self.passkey = settings.MPESA_PASSKEY
        self.callback_url = settings.MPESA_CALLBACK_URL
        self.access_token = None
        self.token_expiry = None
        
    def get_access_token(self):
        """Get M-Pesa access token"""
        if self.access_token and self.token_expiry > timezone.now():
            return self.access_token
        
        auth = (self.consumer_key, self.consumer_secret)
        url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        
        try:
            response = requests.get(url, auth=auth)
            if response.status_code == 200:
                self.access_token = response.json()['access_token']
                self.token_expiry = timezone.now() + timedelta(minutes=59)
                return self.access_token
        except Exception as e:
            logger.error(f"Error getting M-Pesa token: {e}")
            return None
    
    def stk_push(self, phone, amount, description="Deposit to Quantum Capital"):
        """
        Initiate STK Push for M-Pesa payment
        
        Args:
            phone: Phone number (format: 254XXXXXXXXX)
            amount: Amount in KES
            description: Transaction description
            
        Returns:
            dict with checkout_request_id and response_code
        """
        access_token = self.get_access_token()
        if not access_token:
            return {'success': False, 'error': 'Failed to get access token'}
        
        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password = f"{self.shortcode}{self.passkey}{timestamp}"
        
        # Base64 encode password
        import base64
        password_encoded = base64.b64encode(password.encode()).decode()
        
        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password_encoded,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone,
            "PartyB": self.shortcode,
            "PhoneNumber": phone,
            "CallBackURL": self.callback_url,
            "AccountReference": "QuantumCapital",
            "TransactionDesc": description
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'checkout_request_id': data.get('CheckoutRequestID'),
                    'response_code': data.get('ResponseCode'),
                    'response_description': data.get('ResponseDescription')
                }
            else:
                logger.error(f"M-Pesa STK Push error: {response.text}")
                return {'success': False, 'error': response.json().get('errorMessage')}
        except Exception as e:
            logger.error(f"M-Pesa STK Push exception: {e}")
            return {'success': False, 'error': str(e)}
    
    def query_transaction_status(self, checkout_request_id):
        """
        Query M-Pesa transaction status
        
        Args:
            checkout_request_id: The checkout request ID from STK push
            
        Returns:
            dict with transaction status
        """
        access_token = self.get_access_token()
        if not access_token:
            return {'success': False, 'error': 'Failed to get access token'}
        
        url = "https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password = f"{self.shortcode}{self.passkey}{timestamp}"
        
        import base64
        password_encoded = base64.b64encode(password.encode()).decode()
        
        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password_encoded,
            "Timestamp": timestamp,
            "CheckoutRequestID": checkout_request_id
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'result_code': data.get('ResultCode'),
                    'result_desc': data.get('ResultDesc'),
                    'merchant_request_id': data.get('MerchantRequestID')
                }
            else:
                return {'success': False, 'error': response.json().get('errorMessage')}
        except Exception as e:
            logger.error(f"M-Pesa query exception: {e}")
            return {'success': False, 'error': str(e)}
    
    def b2c_withdrawal(self, phone, amount, description="Withdrawal from Quantum Capital"):
        """
        Process B2C withdrawal to M-Pesa
        
        Args:
            phone: Phone number (format: 254XXXXXXXXX)
            amount: Amount in KES
            description: Transaction description
            
        Returns:
            dict with transaction details
        """
        access_token = self.get_access_token()
        if not access_token:
            return {'success': False, 'error': 'Failed to get access token'}
        
        url = "https://sandbox.safaricom.co.ke/mpesa/b2c/v1/paymentrequest"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Use B2C initiator credentials
        payload = {
            "OriginatorConversationID": f"QC-{int(timezone.now().timestamp())}",
            "InitiatorName": settings.MPESA_B2C_INITIATOR,
            "SecurityCredential": settings.MPESA_B2C_SECURITY_CREDENTIAL,
            "CommandID": "BusinessPayment",
            "Amount": int(amount),
            "PartyA": self.shortcode,
            "PartyB": phone,
            "Remarks": description,
            "QueueTimeOutURL": self.callback_url,
            "ResultURL": self.callback_url,
            "Occasion": "Withdrawal"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'conversation_id': data.get('OriginatorConversationID'),
                    'response_code': data.get('ResponseCode'),
                    'response_description': data.get('ResponseDescription')
                }
            else:
                logger.error(f"M-Pesa B2C error: {response.text}")
                return {'success': False, 'error': response.json().get('errorMessage')}
        except Exception as e:
            logger.error(f"M-Pesa B2C exception: {e}")
            return {'success': False, 'error': str(e)}


class CryptoIntegration:
    """Crypto payment integration (USDT, Bitcoin, etc.)"""
    
    def __init__(self):
        self.api_key = settings.CRYPTO_API_KEY
        self.api_secret = settings.CRYPTO_API_SECRET
        self.exchange_rate_api = "https://api.coingecko.com/api/v3"
        
    def get_exchange_rate(self, crypto_symbol="USDT", fiat="KES"):
        """
        Get current exchange rate
        
        Args:
            crypto_symbol: Cryptocurrency symbol (USDT, BTC, ETH)
            fiat: Fiat currency (KES)
            
        Returns:
            dict with rate and timestamp
        """
        crypto_map = {
            'USDT': 'tether',
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'USDC': 'usd-coin'
        }
        
        crypto_id = crypto_map.get(crypto_symbol, 'tether')
        
        try:
            url = f"{self.exchange_rate_api}/simple/price"
            params = {
                'ids': crypto_id,
                'vs_currencies': fiat.lower(),
                'include_24hr_change': 'true'
            }
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                rate = data.get(crypto_id, {}).get(fiat.lower())
                return {
                    'success': True,
                    'symbol': crypto_symbol,
                    'rate': rate,
                    'fiat': fiat,
                    'timestamp': datetime.now().isoformat(),
                    'change_24h': data.get(crypto_id, {}).get(f"{fiat.lower()}_24h_change")
                }
            else:
                logger.error(f"Exchange rate API error: {response.text}")
                return {'success': False, 'error': 'Failed to fetch exchange rate'}
        except Exception as e:
            logger.error(f"Exchange rate exception: {e}")
            return {'success': False, 'error': str(e)}
    
    def generate_wallet_address(self, crypto_symbol, user_id):
        """
        Generate or retrieve wallet address for user
        
        Args:
            crypto_symbol: Cryptocurrency symbol
            user_id: User ID
            
        Returns:
            dict with wallet address
        """
        # In production, this would call a proper wallet service
        # For now, we're storing in Deposit model
        return {
            'success': True,
            'symbol': crypto_symbol,
            'user_id': user_id,
            'address': f"0x{user_id.replace('-', '').lower()}{crypto_symbol.lower()}",  # Placeholder
            'expires_in': 3600
        }
    
    def verify_transaction(self, txid, crypto_symbol):
        """
        Verify crypto transaction on blockchain
        
        Args:
            txid: Transaction hash/ID
            crypto_symbol: Cryptocurrency symbol
            
        Returns:
            dict with transaction confirmation status
        """
        # In production, this would query blockchain explorers
        # Using BlockScout, Etherscan, BlockChair, etc.
        return {
            'success': True,
            'txid': txid,
            'confirmed': True,
            'confirmations': 6,
            'timestamp': datetime.now().isoformat()
        }


class PaymentVerificationService:
    """Unified payment verification service"""
    
    def __init__(self):
        self.mpesa = MPesaIntegration()
        self.crypto = CryptoIntegration()
    
    def verify_deposit(self, deposit_id, method):
        """
        Verify deposit payment
        
        Args:
            deposit_id: Deposit record ID
            method: Payment method (mpesa, bitcoin, usdt_erc20, usdt_trc20)
            
        Returns:
            dict with verification result
        """
        try:
            deposit = Deposit.objects.get(id=deposit_id)
            
            if method == 'mpesa':
                result = self.mpesa.query_transaction_status(
                    deposit.mpesa_checkout_request_id
                )
                
                if result.get('success') and result.get('result_code') == '0':
                    deposit.status = 'confirmed'
                    deposit.confirmed_at = timezone.now()
                    deposit.save()
                    
                    # Update user balance
                    balance = Balance.objects.get(user=deposit.user)
                    balance.total_deposited += deposit.amount
                    balance.current_balance += deposit.amount
                    balance.save()
                    
                    # Create transaction record
                    Transaction.objects.create(
                        user=deposit.user,
                        transaction_type='deposit',
                        amount=deposit.amount,
                        status='completed',
                        payment_method='mpesa',
                        receipt_id=deposit.id,
                        reference=result.get('merchant_request_id'),
                        completed_at=timezone.now()
                    )
                    
                    return {'success': True, 'status': 'confirmed', 'message': 'Deposit confirmed'}
                else:
                    return {'success': False, 'status': 'pending', 'message': 'Payment pending'}
            
            elif method in ['usdt_erc20', 'usdt_trc20', 'bitcoin']:
                result = self.crypto.verify_transaction(
                    deposit.crypto_txid,
                    method.replace('_', ' ').upper()
                )
                
                if result.get('confirmed'):
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
                        payment_method=method,
                        receipt_id=deposit.id,
                        reference=result.get('txid'),
                        completed_at=timezone.now()
                    )
                    
                    return {'success': True, 'status': 'confirmed', 'message': 'Deposit confirmed'}
                else:
                    return {'success': False, 'status': 'pending', 'message': 'Awaiting confirmations'}
            
            return {'success': False, 'error': 'Unknown payment method'}
        
        except Deposit.DoesNotExist:
            return {'success': False, 'error': 'Deposit not found'}
        except Exception as e:
            logger.error(f"Verification error: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_payment_status(self, transaction_id):
        """Get status of any payment"""
        try:
            tx = Transaction.objects.get(id=transaction_id)
            return {
                'success': True,
                'transaction_id': tx.id,
                'user_id': tx.user.user_id,
                'type': tx.transaction_type,
                'amount': str(tx.amount),
                'status': tx.status,
                'method': tx.payment_method,
                'created_at': tx.created_at.isoformat(),
                'completed_at': tx.completed_at.isoformat() if tx.completed_at else None,
                'reference': tx.reference
            }
        except Transaction.DoesNotExist:
            return {'success': False, 'error': 'Transaction not found'}


class ReportingService:
    """Generate financial reports with calculations"""
    
    @staticmethod
    def generate_daily_report(date):
        """Generate daily platform report"""
        from django.db.models import Sum
        
        start = datetime.combine(date, datetime.min.time())
        end = datetime.combine(date, datetime.max.time())
        
        deposits = Transaction.objects.filter(
            transaction_type='deposit', status='completed',
            created_at__range=[start, end]
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal(0)
        
        withdrawals = Transaction.objects.filter(
            transaction_type='withdrawal', status='completed',
            created_at__range=[start, end]
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal(0)
        
        profits = Transaction.objects.filter(
            transaction_type='profit', status='completed',
            created_at__range=[start, end]
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal(0)
        
        fees = Transaction.objects.filter(
            transaction_type='fee', status='completed',
            created_at__range=[start, end]
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal(0)
        
        new_users = User.objects.filter(created_at__range=[start, end]).count()
        
        return {
            'date': date.isoformat(),
            'total_deposits': str(deposits),
            'total_withdrawals': str(withdrawals),
            'total_profits': str(profits),
            'total_fees': str(fees),
            'net_revenue': str(fees),
            'new_users': new_users,
            'aum': str(deposits - withdrawals + profits)
        }
    
    @staticmethod
    def generate_user_profit_statement(user, start_date, end_date):
        """Generate profit statement for user"""
        deposits = Transaction.objects.filter(
            user=user, transaction_type='deposit', status='completed',
            created_at__range=[start_date, end_date]
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal(0)
        
        withdrawals = Transaction.objects.filter(
            user=user, transaction_type='withdrawal', status='completed',
            created_at__range=[start_date, end_date]
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal(0)
        
        profits = Transaction.objects.filter(
            user=user, transaction_type='profit', status='completed',
            created_at__range=[start_date, end_date]
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal(0)
        
        fees = Transaction.objects.filter(
            user=user, transaction_type='fee', status='completed',
            created_at__range=[start_date, end_date]
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal(0)
        
        return {
            'user_id': user.user_id,
            'email': user.email,
            'period_start': start_date.isoformat(),
            'period_end': end_date.isoformat(),
            'total_deposits': str(deposits),
            'total_withdrawals': str(withdrawals),
            'total_profits': str(profits),
            'platform_fees': str(fees),
            'net_profit': str(profits - fees),
            'currency': 'KES'
        }
