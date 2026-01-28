from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AdminDashboardView, UserManagementViewSet, WithdrawalManagementViewSet,
    SystemConfigurationViewSet, ReportingViewSet, TransactionAdjustmentViewSet
)
from .additional_views import (
    edit_user, user_activity_logs, export_users_excel, 
    export_transactions_excel, platform_revenue_report
)

router = DefaultRouter()
router.register(r'dashboard', AdminDashboardView, basename='admin-dashboard')
router.register(r'users', UserManagementViewSet, basename='user-management')
router.register(r'withdrawals', WithdrawalManagementViewSet, basename='withdrawal-management')
router.register(r'config', SystemConfigurationViewSet, basename='system-config')
router.register(r'reports', ReportingViewSet, basename='reporting')
router.register(r'transactions', TransactionAdjustmentViewSet, basename='transaction-adjustment')

urlpatterns = [
    path('', include(router.urls)),
    # Additional admin endpoints
    path('users/edit/', edit_user, name='edit-user'),
    path('users/activity-logs/', user_activity_logs, name='user-activity-logs'),
    path('export/users/', export_users_excel, name='export-users'),
    path('export/transactions/', export_transactions_excel, name='export-transactions'),
    path('revenue/report/', platform_revenue_report, name='revenue-report'),
]
