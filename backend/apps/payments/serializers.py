from rest_framework import serializers
from django.utils import timezone
from .models import Transaction, Deposit, Withdrawal, Balance, MINIMUM_DEPOSIT, MAXIMUM_WITHDRAWAL


class BalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Balance
        fields = ('total_deposited', 'total_withdrawn', 'total_profit', 'total_fees', 'current_balance', 'updated_at')
        read_only_fields = ('total_deposited', 'total_withdrawn', 'total_profit', 'total_fees', 'current_balance', 'updated_at')


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('id', 'transaction_type', 'status', 'amount', 'payment_method', 'description', 'receipt_id', 'reference', 'created_at', 'completed_at')
        read_only_fields = ('id', 'receipt_id', 'created_at', 'completed_at')


class DepositSerializer(serializers.ModelSerializer):
    transaction = TransactionSerializer(read_only=True)
    
    class Meta:
        model = Deposit
        fields = ('id', 'amount', 'payment_method', 'status', 'transaction', 'created_at', 'confirmed_at')
        read_only_fields = ('id', 'status', 'transaction', 'created_at', 'confirmed_at')
    
    def validate_amount(self, value):
        if value < MINIMUM_DEPOSIT:
            raise serializers.ValidationError(f"Minimum deposit is KES {MINIMUM_DEPOSIT}")
        return value
    
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        deposit = Deposit.objects.create(**validated_data)
        
        # Create linked transaction
        import secrets
        receipt_id = f"DEP-{user.user_id}-{secrets.token_hex(4).upper()}"
        transaction = Transaction.objects.create(
            user=user,
            transaction_type='deposit',
            amount=deposit.amount,
            payment_method=deposit.payment_method,
            status='pending',
            receipt_id=receipt_id,
            description=f"Deposit via {deposit.payment_method}"
        )
        deposit.transaction = transaction
        deposit.save(update_fields=['transaction'])
        
        return deposit


class WithdrawalSerializer(serializers.ModelSerializer):
    transaction = TransactionSerializer(read_only=True)
    
    class Meta:
        model = Withdrawal
        fields = ('id', 'amount', 'payment_method', 'status', 'transaction', 'created_at', 'completed_at')
        read_only_fields = ('id', 'status', 'transaction', 'created_at', 'completed_at')
    
    def validate_amount(self, value):
        if value > MAXIMUM_WITHDRAWAL:
            raise serializers.ValidationError(f"Maximum withdrawal per transaction is KES {MAXIMUM_WITHDRAWAL}")
        return value
    
    def create(self, validated_data):
        user = self.context['request'].user
        
        # Check available balance
        balance = Balance.objects.get(user=user)
        if validated_data['amount'] > balance.current_balance:
            raise serializers.ValidationError("Insufficient balance")
        
        validated_data['user'] = user
        withdrawal = Withdrawal.objects.create(**validated_data)
        
        # Create linked transaction
        import secrets
        receipt_id = f"WTH-{user.user_id}-{secrets.token_hex(4).upper()}"
        transaction = Transaction.objects.create(
            user=user,
            transaction_type='withdrawal',
            amount=withdrawal.amount,
            payment_method=withdrawal.payment_method,
            status='pending',
            receipt_id=receipt_id,
            description=f"Withdrawal to {withdrawal.payment_method}"
        )
        withdrawal.transaction = transaction
        withdrawal.save(update_fields=['transaction'])
        
        return withdrawal


class TransactionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('id', 'transaction_type', 'status', 'amount', 'payment_method', 'description', 'receipt_id', 'created_at', 'completed_at')
        read_only_fields = ('id', 'receipt_id', 'created_at', 'completed_at')
