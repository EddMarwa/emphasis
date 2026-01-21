from rest_framework import serializers
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'email', 'phone', 
            'country_code', 'password', 'confirm_password',
            'date_of_birth', 'referral_code'
        )
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
            'phone': {'required': True},
            'country_code': {'required': True},
            'date_of_birth': {'required': False},
            'referral_code': {'required': False},
        }
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return value
    
    def validate_country_code(self, value):
        # Add validation for valid country codes if needed
        if not value or len(value) != 2:
            raise serializers.ValidationError("Country code must be 2 characters.")
        return value.upper()
    
    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError({
                'confirm_password': "Passwords do not match."
            })
        return attrs
    
    def create(self, validated_data):
        # Remove confirm_password from validated_data
        validated_data.pop('confirm_password', None)
        
        # Extract password and hash it
        password = validated_data.pop('password')
        
        # Generate user_id based on country_code
        country_code = validated_data.get('country_code', 'KE')
        user_id = User.generate_user_id(country_code)
        
        # Generate referral code
        referral_code = User.generate_referral_code()
        while User.objects.filter(referral_code=referral_code).exists():
            referral_code = User.generate_referral_code()
        
        # Create user
        user = User.objects.create(
            user_id=user_id,
            referral_code=referral_code,
            **validated_data
        )
        user.set_password(password)
        user.save()
        
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'user_id', 'email', 'phone', 'first_name', 'last_name',
            'country_code', 'account_status', 'kyc_status',
            'email_verified', 'phone_verified', 'created_at'
        )
        read_only_fields = ('user_id', 'created_at')


class UserLoginSerializer(serializers.Serializer):
    email_or_user_id = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    
    def validate_email_or_user_id(self, value):
        if not value:
            raise serializers.ValidationError("Email or User ID is required.")
        return value

