from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from .models import User


class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that works with our custom User model
    """
    def get_user(self, validated_token):
        try:
            user_id = validated_token['user_id']
        except KeyError:
            raise InvalidToken('Token contained no recognizable user identification')
        
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found')
        
        if not user.account_status == 'active':
            raise AuthenticationFailed('User account is not active')
        
        return user

