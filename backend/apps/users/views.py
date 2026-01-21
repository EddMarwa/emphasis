from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from .models import User
from .serializers import (
    UserRegistrationSerializer, 
    UserSerializer, 
    UserLoginSerializer
)


def get_tokens_for_user(user):
    """Generate JWT tokens for user"""
    refresh = RefreshToken()
    refresh['user_id'] = user.user_id
    refresh['email'] = user.email
    
    access_token = refresh.access_token
    access_token['user_id'] = user.user_id
    access_token['email'] = user.email
    
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
        tokens = get_tokens_for_user(user)
        
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
    tokens = get_tokens_for_user(user)
    
    # Serialize user data
    user_data = UserSerializer(user).data
    
    return Response({
        'user_id': user.user_id,
        'user': user_data,
        'access': tokens['access'],
        'refresh': tokens['refresh'],
        'message': 'Login successful'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_current_user_view(request):
    """
    Get current authenticated user
    GET /api/auth/user/
    """
    # The user is already authenticated via CustomJWTAuthentication
    # request.user should be a User instance
    if hasattr(request.user, 'user_id'):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(
            {'detail': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )

