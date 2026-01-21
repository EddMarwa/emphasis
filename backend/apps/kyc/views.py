from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta

from .models import KYCDocument, KYCVerificationLog, KYCRejectionTemplate, KYCWithdrawalLimit
from .serializers import (
    KYCDocumentSerializer, KYCSubmissionSerializer, KYCVerificationLogSerializer,
    KYCRejectionTemplateSerializer, KYCWithdrawalLimitSerializer
)
from apps.admin_panel.models import AdminUser


class KYCDocumentViewSet(viewsets.ViewSet):
    """User KYC document management"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def my_kyc(self, request):
        """Get current user's KYC status"""
        try:
            kyc = KYCDocument.objects.get(user=request.user)
            serializer = KYCDocumentSerializer(kyc)
            return Response(serializer.data)
        except KYCDocument.DoesNotExist:
            return Response({'status': 'not_started'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def submit_kyc(self, request):
        """Submit or resubmit KYC documents"""
        serializer = KYCSubmissionSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            kyc_doc = serializer.save()
            
            # Log submission
            KYCVerificationLog.objects.create(
                kyc=kyc_doc,
                action='submitted',
                old_status=kyc_doc.status,
                new_status='pending',
                notes='User submitted KYC documents'
            )
            
            # Try auto-verification
            self._auto_verify_kyc(kyc_doc)
            
            kyc_doc.save()
            return Response(KYCDocumentSerializer(kyc_doc).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @staticmethod
    def _auto_verify_kyc(kyc_doc):
        """Auto-verify KYC based on document quality and information"""
        # Placeholder for AI/ML verification logic
        # In production, integrate with document verification APIs (e.g., Trulioo, IDology)
        
        verification_score = 0
        
        # Check if all required fields are filled
        if all([kyc_doc.full_name, kyc_doc.date_of_birth, kyc_doc.document_number,
                kyc_doc.address_line1, kyc_doc.city, kyc_doc.country, kyc_doc.selfie_url]):
            verification_score += 30
        
        # Check if documents are present
        if kyc_doc.document_front_url:
            verification_score += 30
        if kyc_doc.address_proof_url:
            verification_score += 20
        if kyc_doc.selfie_url:
            verification_score += 20
        
        # Auto-approve if score > 80 (if enabled in config)
        from apps.admin_panel.models import SystemConfiguration
        config = SystemConfiguration.get_config()
        
        if config.kyc_auto_approve_documents and verification_score >= 80:
            kyc_doc.status = 'approved'
            kyc_doc.verification_level = 2
            kyc_doc.verification_date = timezone.now()
            kyc_doc.expiry_date = timezone.now() + timedelta(days=365*config.kyc_expiry_months)
            
            KYCVerificationLog.objects.create(
                kyc=kyc_doc,
                action='auto_approved',
                old_status='pending',
                new_status='approved',
                verification_score=verification_score,
                notes=f'Auto-approved with score {verification_score}'
            )
        else:
            kyc_doc.status = 'pending'
            KYCVerificationLog.objects.create(
                kyc=kyc_doc,
                action='submitted',
                old_status='not_started',
                new_status='pending',
                verification_score=verification_score,
                notes=f'Manual review required - score {verification_score}'
            )


class KYCVerificationViewSet(viewsets.ViewSet):
    """Admin KYC verification and management"""
    
    def get_permissions(self):
        """Check if user is admin with KYC verification rights"""
        if self.action in ['approve_kyc', 'reject_kyc', 'list_pending']:
            return [IsAuthenticated()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def list_pending(self, request):
        """List pending KYC documents for admin"""
        try:
            admin = AdminUser.objects.get(user=request.user)
            if not admin.can_verify_kyc:
                return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        except AdminUser.DoesNotExist:
            return Response({'error': 'Not an admin'}, status=status.HTTP_403_FORBIDDEN)
        
        pending_kyc = KYCDocument.objects.filter(status='pending').order_by('submitted_at')
        serializer = KYCDocumentSerializer(pending_kyc, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def approve_kyc(self, request):
        """Approve KYC document"""
        try:
            admin = AdminUser.objects.get(user=request.user)
            if not admin.can_verify_kyc:
                return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        except AdminUser.DoesNotExist:
            return Response({'error': 'Not an admin'}, status=status.HTTP_403_FORBIDDEN)
        
        kyc_id = request.data.get('kyc_id')
        verification_level = request.data.get('verification_level', 2)
        notes = request.data.get('notes', '')
        
        try:
            kyc = KYCDocument.objects.get(id=kyc_id)
            kyc.status = 'approved'
            kyc.verification_level = verification_level
            kyc.verified_by = admin
            kyc.verification_date = timezone.now()
            kyc.expiry_date = timezone.now() + timedelta(days=365)  # 1 year expiry
            kyc.save()
            
            # Log action
            KYCVerificationLog.objects.create(
                kyc=kyc,
                action='manual_approved',
                performed_by=admin,
                old_status='pending',
                new_status='approved',
                notes=notes,
                verification_score=100
            )
            
            return Response({'message': f'KYC for {kyc.user.user_id} approved'})
        except KYCDocument.DoesNotExist:
            return Response({'error': 'KYC not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def reject_kyc(self, request):
        """Reject KYC document"""
        try:
            admin = AdminUser.objects.get(user=request.user)
            if not admin.can_verify_kyc:
                return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        except AdminUser.DoesNotExist:
            return Response({'error': 'Not an admin'}, status=status.HTTP_403_FORBIDDEN)
        
        kyc_id = request.data.get('kyc_id')
        rejection_reason = request.data.get('rejection_reason', '')
        template_code = request.data.get('template_code')
        
        try:
            kyc = KYCDocument.objects.get(id=kyc_id)
            kyc.status = 'rejected'
            kyc.verified_by = admin
            kyc.verification_date = timezone.now()
            
            # Use template if provided
            if template_code:
                try:
                    template = KYCRejectionTemplate.objects.get(code=template_code)
                    kyc.rejection_reason = template.message
                except KYCRejectionTemplate.DoesNotExist:
                    kyc.rejection_reason = rejection_reason
            else:
                kyc.rejection_reason = rejection_reason
            
            kyc.save()
            
            # Log action
            KYCVerificationLog.objects.create(
                kyc=kyc,
                action='rejected',
                performed_by=admin,
                old_status='pending',
                new_status='rejected',
                notes=rejection_reason
            )
            
            return Response({'message': f'KYC for {kyc.user.user_id} rejected'})
        except KYCDocument.DoesNotExist:
            return Response({'error': 'KYC not found'}, status=status.HTTP_404_NOT_FOUND)


class KYCConfigViewSet(viewsets.ViewSet):
    """KYC configuration management"""
    
    @action(detail=False, methods=['get'])
    def rejection_templates(self, request):
        """Get all active rejection templates"""
        templates = KYCRejectionTemplate.objects.filter(is_active=True)
        serializer = KYCRejectionTemplateSerializer(templates, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def withdrawal_limits(self, request):
        """Get KYC withdrawal limits"""
        limits = KYCWithdrawalLimit.objects.all()
        serializer = KYCWithdrawalLimitSerializer(limits, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def user_limits(self, request):
        """Get withdrawal limit for current user"""
        try:
            kyc = KYCDocument.objects.get(user=request.user)
            if kyc.status == 'approved':
                limit = KYCWithdrawalLimit.objects.get(verification_level=kyc.verification_level)
                serializer = KYCWithdrawalLimitSerializer(limit)
                return Response({
                    'kyc_status': 'approved',
                    'verification_level': kyc.verification_level,
                    'limits': serializer.data
                })
            else:
                return Response({'kyc_status': 'not_approved'}, status=status.HTTP_403_FORBIDDEN)
        except KYCDocument.DoesNotExist:
            return Response({'kyc_status': 'not_started'}, status=status.HTTP_404_NOT_FOUND)
