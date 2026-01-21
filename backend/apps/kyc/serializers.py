from rest_framework import serializers
from .models import KYCDocument, KYCVerificationLog, KYCRejectionTemplate, KYCWithdrawalLimit


class KYCDocumentSerializer(serializers.ModelSerializer):
    """Serializer for KYC documents"""
    user_id = serializers.CharField(source='user.user_id', read_only=True)
    verified_by_name = serializers.CharField(source='verified_by.user.username', read_only=True)
    
    class Meta:
        model = KYCDocument
        fields = ['id', 'user_id', 'full_name', 'date_of_birth', 'nationality',
                  'document_type', 'document_number', 'document_front_url', 'document_back_url',
                  'address_line1', 'address_line2', 'city', 'state_province', 'postal_code',
                  'country', 'address_proof_url', 'selfie_url', 'status', 'verification_level',
                  'verified_by_name', 'verification_date', 'expiry_date', 'rejection_reason',
                  'submitted_at', 'updated_at', 'is_expired', 'needs_resubmission']
        read_only_fields = ['id', 'verified_by_name', 'verification_date', 'expiry_date',
                            'submitted_at', 'updated_at', 'is_expired']


class KYCSubmissionSerializer(serializers.ModelSerializer):
    """Serializer for KYC document submission"""
    class Meta:
        model = KYCDocument
        fields = ['full_name', 'date_of_birth', 'nationality', 'document_type',
                  'document_number', 'document_front_url', 'document_back_url',
                  'address_line1', 'address_line2', 'city', 'state_province',
                  'postal_code', 'country', 'address_proof_url', 'selfie_url']
    
    def create(self, validated_data):
        """Create KYC document"""
        user = self.context['request'].user
        kyc_doc, created = KYCDocument.objects.get_or_create(
            user=user,
            defaults=validated_data
        )
        if not created:
            # Update existing document
            for key, value in validated_data.items():
                setattr(kyc_doc, key, value)
            kyc_doc.status = 'pending'
            kyc_doc.save()
        
        return kyc_doc


class KYCVerificationLogSerializer(serializers.ModelSerializer):
    """Serializer for KYC verification logs"""
    performed_by_name = serializers.CharField(source='performed_by.user.username', read_only=True)
    
    class Meta:
        model = KYCVerificationLog
        fields = ['id', 'action', 'performed_by_name', 'notes', 'old_status', 'new_status',
                  'verification_score', 'created_at']
        read_only_fields = ['performed_by_name', 'created_at']


class KYCRejectionTemplateSerializer(serializers.ModelSerializer):
    """Serializer for rejection templates"""
    class Meta:
        model = KYCRejectionTemplate
        fields = ['id', 'code', 'title', 'message', 'category', 'is_active']


class KYCWithdrawalLimitSerializer(serializers.ModelSerializer):
    """Serializer for withdrawal limits"""
    class Meta:
        model = KYCWithdrawalLimit
        fields = ['id', 'verification_level', 'daily_limit', 'monthly_limit',
                  'transaction_limit', 'description']
