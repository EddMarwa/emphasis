from django.db import models
from apps.users.models import User


# Platform settings for minimum/maximum rules
MINIMUM_DEPOSIT = 10000  # 10k KES
MAXIMUM_WITHDRAWAL = 500000  # 500k KES per transaction
PLATFORM_FEE_PERCENT = 10  # 10% of profits


class PaymentMethod(models.Model):
    """Payment method choices"""
    PAYMENT_CHOICES = [
        ('mpesa', 'M-Pesa'),
        ('usdt_trc20', 'USDT TRC20'),
        ('usdt_erc20', 'USDT ERC20'),
        ('bitcoin', 'Bitcoin'),
    ]
    name = models.CharField(max_length=50, choices=PAYMENT_CHOICES, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'payment_methods'
    
    def __str__(self):
        return self.name


class Transaction(models.Model):
    """All financial transactions"""
    TRANSACTION_TYPE_CHOICES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('profit', 'Profit'),
        ('fee', 'Platform Fee'),
        ('bonus', 'Referral Bonus'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    receipt_id = models.CharField(max_length=100, unique=True)
    reference = models.CharField(max_length=100, blank=True, null=True)  # External reference (M-Pesa ID, tx hash, etc.)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'transactions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.user_id} - {self.transaction_type} - {self.amount} KES"


class Deposit(models.Model):
    """Deposit records"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deposits')
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    mpesa_request_id = models.CharField(max_length=100, blank=True, null=True)
    mpesa_checkout_request_id = models.CharField(max_length=255, blank=True, null=True)
    crypto_wallet = models.CharField(max_length=255, blank=True, null=True)
    crypto_txid = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'deposits'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.user_id} - {self.amount} KES ({self.payment_method})"


class Withdrawal(models.Model):
    """Withdrawal records"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='withdrawals')
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    mpesa_phone = models.CharField(max_length=20, blank=True, null=True)
    crypto_wallet = models.CharField(max_length=255, blank=True, null=True)
    rejection_reason = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'withdrawals'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.user_id} - {self.amount} KES ({self.payment_method})"


class Balance(models.Model):
    """User account balance snapshot"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='balance')
    total_deposited = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_withdrawn = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_fees = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    current_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'balances'
    
    def __str__(self):
        return f"{self.user.user_id} - {self.current_balance} KES"
    
    @staticmethod
    def calculate_balance(user):
        """Calculate balance from transactions"""
        deposits = Transaction.objects.filter(
            user=user, transaction_type='deposit', status='completed'
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        
        withdrawals = Transaction.objects.filter(
            user=user, transaction_type='withdrawal', status='completed'
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        
        profits = Transaction.objects.filter(
            user=user, transaction_type='profit', status='completed'
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        
        fees = Transaction.objects.filter(
            user=user, transaction_type='fee', status='completed'
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        
        return {
            'total_deposited': deposits,
            'total_withdrawn': withdrawals,
            'total_profit': profits,
            'total_fees': fees,
            'current_balance': deposits - withdrawals + profits - fees
        }
