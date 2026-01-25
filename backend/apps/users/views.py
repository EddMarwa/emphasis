from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Q
import pyotp
from apps.admin_panel.models import AdminUser
from .models import User
from .serializers import (
    UserRegistrationSerializer, 
    UserSerializer, 
    UserLoginSerializer
)

AdminAuthUser = get_user_model()


def get_tokens_with_claims(claims: dict):
    """Generate JWT tokens with the provided claims added to both refresh and access tokens."""
    refresh = RefreshToken()
    for key, value in claims.items():
        refresh[key] = value

    access_token = refresh.access_token
    for key, value in claims.items():
        access_token[key] = value

    return {
        'refresh': str(refresh),
        'access': str(access_token),
    }


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_view(request):
    """
    User registration endpoint
    POST /api/auth/register/
    """
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        
        # Update last_login
        user.last_login = timezone.now()
        user.save()
        
        # Generate tokens
        claims = {
            'user_id': user.user_id,
            'email': user.email,
            'is_admin': False,
        }
        tokens = get_tokens_with_claims(claims)
        
        # Serialize user data
        user_data = UserSerializer(user).data
        
        return Response({
            'user_id': user.user_id,
            'user': user_data,
            'access': tokens['access'],
            'refresh': tokens['refresh'],
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """
    User login endpoint
    Accepts either email or user_id
    POST /api/auth/login/
    """
    serializer = UserLoginSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    email_or_user_id = serializer.validated_data['email_or_user_id']
    password = serializer.validated_data['password']
    otp_code = serializer.validated_data.get('otp_code')

    # --- Admin login path (Django auth users) ---
    admin_candidate = AdminAuthUser.objects.filter(
        Q(username=email_or_user_id) | Q(email=email_or_user_id)
    ).first()

    if admin_candidate:
        has_admin_profile = AdminUser.objects.filter(user=admin_candidate, is_active=True).exists()

        if admin_candidate.check_password(password) and admin_candidate.is_active and has_admin_profile:
            admin_profile = AdminUser.objects.get(user=admin_candidate)
            admin_candidate.last_login = timezone.now()
            admin_candidate.save(update_fields=['last_login'])

            claims = {
                'is_admin': True,
                'admin_id': admin_candidate.id,
                'username': admin_candidate.username,
                'email': admin_candidate.email,
                'role': admin_profile.role,
            }

            tokens = get_tokens_with_claims(claims)

            return Response({
                'admin_id': admin_candidate.id,
                'user': {
                    'id': admin_candidate.id,
                    'username': admin_candidate.username,
                    'email': admin_candidate.email,
                    'is_admin': True,
                    'admin_role': admin_profile.role,
                },
                'access': tokens['access'],
                'refresh': tokens['refresh'],
                'message': 'Login successful'
            }, status=status.HTTP_200_OK)
        # If admin candidate exists but either password or profile invalid, fall through to user login

    # Try to find user by email or user_id
    try:
        if '@' in email_or_user_id:
            # Assume it's an email
            user = User.objects.get(email=email_or_user_id)
        else:
            # Assume it's a user_id
            user = User.objects.get(user_id=email_or_user_id)
    except User.DoesNotExist:
        return Response(
            {'detail': 'Invalid email/User ID or password.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Check password
    if not user.check_password(password):
        return Response(
            {'detail': 'Invalid email/User ID or password.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Enforce 2FA if enabled
    if user.otp_enabled:
        if not user.otp_secret:
            return Response(
                {'detail': 'Two-factor authentication is misconfigured. Please reset 2FA.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        if not otp_code:
            return Response(
                {'detail': 'Two-factor authentication code is required.', 'code_required': True},
                status=status.HTTP_401_UNAUTHORIZED
            )
        totp = pyotp.TOTP(user.otp_secret)
        if not totp.verify(otp_code, valid_window=1):
            return Response(
                {'detail': 'Invalid two-factor authentication code.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
    
    # Check account status
    if user.account_status != 'active':
        return Response(
            {'detail': f'Account is {user.account_status}. Please contact support.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Update last_login
    user.last_login = timezone.now()
    user.save()
    
    # Generate tokens
    claims = {
        'user_id': user.user_id,
        'email': user.email,
        'is_admin': False,
    }

    tokens = get_tokens_with_claims(claims)
    
    # Serialize user data
    user_data = UserSerializer(user).data
    
    return Response({
        'user_id': user.user_id,
        'user': user_data,
        'access': tokens['access'],
        'refresh': tokens['refresh'],
        'message': 'Login successful'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def setup_2fa_view(request):
    """Generate or return TOTP secret and provisioning URI for the current user."""
    user = request.user
    if not user.otp_secret:
        user.otp_secret = pyotp.random_base32()
        user.otp_enabled = False
        user.save(update_fields=['otp_secret', 'otp_enabled'])

    totp = pyotp.TOTP(user.otp_secret)
    provisioning_uri = totp.provisioning_uri(name=user.email or user.user_id, issuer_name='Quantum Capital')

    return Response({
        'secret': user.otp_secret,
        'provisioning_uri': provisioning_uri,
        'otp_enabled': user.otp_enabled,
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def verify_2fa_view(request):
    """Verify a TOTP code and enable 2FA for the current user."""
    code = request.data.get('otp_code')
    user = request.user

    if not user.otp_secret:
        return Response({'detail': '2FA is not initialized.'}, status=status.HTTP_400_BAD_REQUEST)
    if not code:
        return Response({'detail': 'otp_code is required.'}, status=status.HTTP_400_BAD_REQUEST)

    totp = pyotp.TOTP(user.otp_secret)
    if not totp.verify(code, valid_window=1):
        return Response({'detail': 'Invalid code.'}, status=status.HTTP_401_UNAUTHORIZED)

    user.otp_enabled = True
    user.save(update_fields=['otp_enabled'])
    return Response({'message': '2FA enabled', 'otp_enabled': True}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def disable_2fa_view(request):
    """Disable 2FA and clear secret for the current user."""
    user = request.user
    user.otp_enabled = False
    user.otp_secret = None
    user.save(update_fields=['otp_enabled', 'otp_secret'])
    return Response({'message': '2FA disabled', 'otp_enabled': False}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_current_user_view(request):
    """
    Get current authenticated user (supports both regular users and admins)
    GET /api/auth/user/
    """
    # Regular users (custom User model)
    if hasattr(request.user, 'user_id'):
        serializer = UserSerializer(request.user)
        data = serializer.data
        data['is_admin'] = False
        return Response(data, status=status.HTTP_200_OK)

    # Admin users (Django auth + AdminUser profile)
    try:
        admin_profile = AdminUser.objects.get(user=request.user, is_active=True)
        return Response({
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'is_admin': True,
            'admin_role': admin_profile.role,
        }, status=status.HTTP_200_OK)
    except AdminUser.DoesNotExist:
        return Response(
            {'detail': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )

