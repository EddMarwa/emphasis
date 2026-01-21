from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.http import HttpResponse
from django.db.models import Q
import csv
from io import StringIO
from .models import Transaction, Deposit, Withdrawal, Balance
from .serializers import (
    TransactionSerializer, TransactionListSerializer, 
    DepositSerializer, WithdrawalSerializer, BalanceSerializer
)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def balance_view(request):
    """Get user balance"""
    user = request.user
    balance, created = Balance.objects.get_or_create(user=user)
    
    # Recalculate balance from transactions
    balance_data = Balance.calculate_balance(user)
    for key, value in balance_data.items():
        setattr(balance, key, value)
    balance.save()
    
    serializer = BalanceSerializer(balance)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def deposit_list_view(request):
    """List deposits or create deposit request"""
    user = request.user
    
    if request.method == 'GET':
        deposits = Deposit.objects.filter(user=user)
        serializer = DepositSerializer(deposits, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        serializer = DepositSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def deposit_detail_view(request, deposit_id):
    """Get deposit details"""
    user = request.user
    try:
        deposit = Deposit.objects.get(id=deposit_id, user=user)
    except Deposit.DoesNotExist:
        return Response({'detail': 'Deposit not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = DepositSerializer(deposit)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def withdrawal_list_view(request):
    """List withdrawals or create withdrawal request"""
    user = request.user
    
    if request.method == 'GET':
        withdrawals = Withdrawal.objects.filter(user=user)
        serializer = WithdrawalSerializer(withdrawals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        serializer = WithdrawalSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def withdrawal_detail_view(request, withdrawal_id):
    """Get withdrawal details"""
    user = request.user
    try:
        withdrawal = Withdrawal.objects.get(id=withdrawal_id, user=user)
    except Withdrawal.DoesNotExist:
        return Response({'detail': 'Withdrawal not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = WithdrawalSerializer(withdrawal)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def transaction_list_view(request):
    """List transactions with filtering and search"""
    user = request.user
    transactions = Transaction.objects.filter(user=user)
    
    # Filtering
    tx_type = request.query_params.get('type')
    if tx_type:
        transactions = transactions.filter(transaction_type=tx_type)
    
    status_filter = request.query_params.get('status')
    if status_filter:
        transactions = transactions.filter(status=status_filter)
    
    # Search
    search = request.query_params.get('search')
    if search:
        transactions = transactions.filter(
            Q(receipt_id__icontains=search) | 
            Q(description__icontains=search) |
            Q(reference__icontains=search)
        )
    
    # Pagination
    page = request.query_params.get('page', 1)
    limit = int(request.query_params.get('limit', 20))
    offset = (int(page) - 1) * limit
    total = transactions.count()
    
    transactions = transactions[offset:offset + limit]
    serializer = TransactionListSerializer(transactions, many=True)
    
    return Response({
        'count': total,
        'page': page,
        'limit': limit,
        'results': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def transaction_export_view(request):
    """Export transactions to CSV"""
    user = request.user
    transactions = Transaction.objects.filter(user=user)
    
    # Apply same filters as list view
    tx_type = request.query_params.get('type')
    if tx_type:
        transactions = transactions.filter(transaction_type=tx_type)
    
    status_filter = request.query_params.get('status')
    if status_filter:
        transactions = transactions.filter(status=status_filter)
    
    # Create CSV
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Receipt ID', 'Type', 'Status', 'Amount (KES)', 'Payment Method', 'Description', 'Created At', 'Completed At'])
    
    for tx in transactions:
        writer.writerow([
            tx.receipt_id,
            tx.transaction_type,
            tx.status,
            tx.amount,
            tx.payment_method or '',
            tx.description or '',
            tx.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            tx.completed_at.strftime('%Y-%m-%d %H:%M:%S') if tx.completed_at else ''
        ])
    
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'
    return response
