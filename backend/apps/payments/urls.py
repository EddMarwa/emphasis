from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('balance/', views.balance_view, name='balance'),
    path('deposits/', views.deposit_list_view, name='deposit-list'),
    path('deposits/<int:deposit_id>/', views.deposit_detail_view, name='deposit-detail'),
    path('withdrawals/', views.withdrawal_list_view, name='withdrawal-list'),
    path('withdrawals/<int:withdrawal_id>/', views.withdrawal_detail_view, name='withdrawal-detail'),
    path('transactions/', views.transaction_list_view, name='transaction-list'),
    path('transactions/export/', views.transaction_export_view, name='transaction-export'),
]
