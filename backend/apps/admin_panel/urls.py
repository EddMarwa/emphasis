from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AdminDashboardView, UserManagementViewSet, WithdrawalManagementViewSet,
    SystemConfigurationViewSet, ReportingViewSet, TransactionAdjustmentViewSet
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
]
