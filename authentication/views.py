# authentication/views.py
import jwt
import time
from django.conf import settings
from django.core.cache import cache
from django.core.management import call_command
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer,
    UserProfileSerializer, UserUpdateSerializer,
    PasswordChangeSerializer
)
from .models import CustomUser
from .schema import (
    change_password_schema, user_profile_schema, logout_schema, check_username_schema, check_email_schema, refresh_token_schema, invalidate_token_schema, register_user_schema, login_user_schema
)

class UserRegistrationView(APIView):
    """User registration endpoint"""
    permission_classes = [permissions.AllowAny]
    
    @register_user_schema
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate tokens for auto-login
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'Registration successful',
                'user': UserProfileSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )

class UserLoginView(TokenObtainPairView):
    """Enhanced login view with user data"""
    
    @login_user_schema
    def post(self, request, *args, **kwargs):
        # Get tokens from parent class
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Get user from token
            serializer = UserLoginSerializer(
                data=request.data,
                context={'request': request}
            )
            if serializer.is_valid():
                user = serializer.validated_data['user']
                response.data['user'] = UserProfileSerializer(user).data
                response.data['message'] = 'Login successful'
        
        return response

# Add to UserProfileView
@user_profile_schema
class UserProfileView(RetrieveUpdateAPIView):
    """User profile view"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return UserUpdateSerializer
        return UserProfileSerializer

class PasswordChangeView(APIView):
    """Password change endpoint"""
    permission_classes = [permissions.IsAuthenticated]
    
    @change_password_schema
    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Password changed successfully'
            }, status=status.HTTP_200_OK)
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

@logout_schema
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def logout_view(request):
    """
    Enhanced logout that immediately invalidates both refresh and access tokens
    """
    try:
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response({
                'error': 'Refresh token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Blacklist the refresh token (your existing logic)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            pass  # Token might already be blacklisted or invalid
        
        # Also blacklist the current access token for immediate effect
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header and auth_header.startswith('Bearer '):
            access_token = auth_header.split(' ')[1]
            try:
                # Decode to get expiry time
                decoded_token = jwt.decode(
                    access_token, 
                    settings.SECRET_KEY, 
                    algorithms=['HS256'],
                    options={"verify_exp": False}  # Don't fail if expired
                )
                
                # Cache blacklist until token would naturally expire
                exp_timestamp = decoded_token.get('exp', 0)
                current_time = int(time.time())
                
                if exp_timestamp > current_time:
                    ttl = exp_timestamp - current_time
                    blacklist_key = f"blacklist_access_token:{access_token}"
                    cache.set(blacklist_key, True, timeout=ttl)
                    
            except (jwt.InvalidTokenError, Exception):
                # If we can't decode, still try to blacklist for default duration
                blacklist_key = f"blacklist_access_token:{access_token}"
                cache.set(blacklist_key, True, timeout=900)  # 15 minutes default
        
        return Response({
            'message': 'Logout successful - all tokens invalidated'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Logout failed',
            'detail': str(e) if settings.DEBUG else 'Invalid token'
        }, status=status.HTTP_400_BAD_REQUEST)

@check_username_schema
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def check_username(request):
    """Check if username is available"""
    username = request.GET.get('username')
    if not username:
        return Response({
            'error': 'Username parameter required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    exists = CustomUser.objects.filter(username=username).exists()
    return Response({
        'available': not exists,
        'username': username
    })

@check_email_schema
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def check_email(request):
    """Check if email is available"""
    email = request.GET.get('email')
    if not email:
        return Response({
            'error': 'Email parameter required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    exists = CustomUser.objects.filter(email=email).exists()
    return Response({
        'available': not exists,
        'email': email
    })

@refresh_token_schema
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def token_refresh_view(request):
    """
    Enhanced token refresh that also checks cache blacklist
    """
    from rest_framework_simplejwt.views import TokenRefreshView
    
    # Use the default refresh logic but add cache invalidation for old access token
    refresh_view = TokenRefreshView()
    response = refresh_view.post(request)
    
    # If successful, blacklist the old access token that was just replaced
    if response.status_code == 200:
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header and auth_header.startswith('Bearer '):
            old_access_token = auth_header.split(' ')[1]
            blacklist_key = f"blacklist_access_token:{old_access_token}"
            cache.set(blacklist_key, True, timeout=900)  # 15 minutes
    
    return response

@invalidate_token_schema
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def invalidate_all_tokens_view(request):
    """Admin endpoint to invalidate all user tokens"""
    # Check if user is admin/superuser
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({
            'error': 'Admin privileges required'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        call_command('invalidate_all_tokens', confirm=True)
        return Response({
            'message': 'All user sessions invalidated successfully'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': 'Failed to invalidate tokens',
            'detail': str(e) if settings.DEBUG else 'Internal error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
