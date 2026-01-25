from django.urls import path
from . import views, payment_api

app_name = 'payments'

urlpatterns = [
    # Balance and transaction endpoints
    path('balance/', views.balance_view, name='balance'),
    path('deposits/', views.deposit_list_view, name='deposit-list'),
    path('deposits/<int:deposit_id>/', views.deposit_detail_view, name='deposit-detail'),
    path('withdrawals/', views.withdrawal_list_view, name='withdrawal-list'),
    path('withdrawals/<int:withdrawal_id>/', views.withdrawal_detail_view, name='withdrawal-detail'),
    path('transactions/', views.transaction_list_view, name='transaction-list'),
    path('transactions/export/', views.transaction_export_view, name='transaction-export'),
    
    # M-Pesa payment endpoints
    path('mpesa/stk-push/', payment_api.initiate_mpesa_payment, name='mpesa-stk-push'),
    path('mpesa/status/', payment_api.check_mpesa_payment, name='mpesa-status'),
    
    # Crypto payment endpoints
    path('crypto/exchange-rate/', payment_api.get_crypto_exchange_rate, name='crypto-exchange-rate'),
    path('crypto/generate-address/', payment_api.generate_crypto_wallet, name='crypto-generate-wallet'),
    path('crypto/verify-deposit/', payment_api.verify_crypto_deposit, name='crypto-verify-deposit'),
    
    # Payment status and reporting
    path('status/', payment_api.get_payment_status, name='payment-status'),
    path('user-transactions/', payment_api.get_user_transactions, name='user-transactions'),
    path('profit-statement/', payment_api.generate_profit_statement, name='profit-statement'),
    path('platform-stats/', payment_api.platform_statistics, name='platform-stats'),
]
