from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import KYCDocumentViewSet, KYCVerificationViewSet, KYCConfigViewSet

router = DefaultRouter()
router.register(r'documents', KYCDocumentViewSet, basename='kyc-documents')
router.register(r'verification', KYCVerificationViewSet, basename='kyc-verification')
router.register(r'config', KYCConfigViewSet, basename='kyc-config')

urlpatterns = [
    path('', include(router.urls)),
]
