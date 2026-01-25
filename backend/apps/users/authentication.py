from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from django.contrib.auth import get_user_model
from .models import User

AdminAuthUser = get_user_model()


class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that works with our custom User model
    """
    def get_user(self, validated_token):
        is_admin = validated_token.get('is_admin', False)

        # Branch for admin tokens (Django auth users)
        if is_admin:
            admin_id = validated_token.get('admin_id')
            if admin_id is None:
                raise InvalidToken('Token missing admin identifier')

            try:
                admin_user = AdminAuthUser.objects.get(id=admin_id)
            except AdminAuthUser.DoesNotExist:
                raise AuthenticationFailed('Admin user not found')

            if not admin_user.is_active:
                raise AuthenticationFailed('Admin account is not active')

            return admin_user

        # Branch for regular users
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

