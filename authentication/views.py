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
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer,
    UserProfileSerializer, UserUpdateSerializer,
    PasswordChangeSerializer
)
from .models import CustomUser

# Response serializers for OpenAPI documentation
from rest_framework import serializers

class UserRegistrationResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    user = UserProfileSerializer()
    tokens = serializers.DictField()

class LoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserProfileSerializer()
    message = serializers.CharField()

class MessageResponseSerializer(serializers.Serializer):
    message = serializers.CharField()

class ErrorResponseSerializer(serializers.Serializer):
    error = serializers.CharField()
    detail = serializers.CharField(required=False)

class AvailabilityResponseSerializer(serializers.Serializer):
    available = serializers.BooleanField()
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)

class TokenRefreshRequestSerializer(serializers.Serializer):
    refresh = serializers.CharField()

class TokenRefreshResponseSerializer(serializers.Serializer):
    access = serializers.CharField()

class LogoutRequestSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

class UserRegistrationView(APIView):
    """User registration endpoint"""
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer
    
    @extend_schema(
        summary="Register new user",
        description="Register a new user account with automatic login",
        tags=['Authentication'],
        request=UserRegistrationSerializer,
        responses={
            201: OpenApiResponse(
                response=UserRegistrationResponseSerializer,
                description="Registration successful",
                examples=[
                    OpenApiExample(
                        'Success',
                        value={
                            'message': 'Registration successful',
                            'user': {'id': 1, 'username': 'john_doe', 'email': 'john@example.com'},
                            'tokens': {'access': 'token...', 'refresh': 'token...'}
                        }
                    )
                ]
            ),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="Validation errors")
        }
    )
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
    serializer_class = UserLoginSerializer
    
    @extend_schema(
        summary="User login",
        description="Authenticate user and return tokens with user profile",
        tags=['Authentication'],
        request=UserLoginSerializer,
        responses={
            200: OpenApiResponse(
                response=LoginResponseSerializer,
                description="Login successful"
            ),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="Invalid credentials")
        }
    )
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

class UserProfileView(RetrieveUpdateAPIView):
    """User profile view"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserProfileSerializer
    
    @extend_schema(
        summary="Get user profile",
        description="Retrieve current user's profile information",
        tags=['Authentication'],
        responses={
            200: OpenApiResponse(response=UserProfileSerializer, description="User profile")
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update user profile",
        description="Update current user's profile information",
        tags=['Authentication'],
        request=UserUpdateSerializer,
        responses={
            200: OpenApiResponse(response=UserProfileSerializer, description="Profile updated")
        }
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        summary="Partially update user profile",
        description="Partially update current user's profile information",
        tags=['Authentication'],
        request=UserUpdateSerializer,
        responses={
            200: OpenApiResponse(response=UserProfileSerializer, description="Profile updated")
        }
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

class PasswordChangeView(APIView):
    """Password change endpoint"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PasswordChangeSerializer
    
    @extend_schema(
        summary="Change password",
        description="Change current user's password",
        tags=['Authentication'],
        request=PasswordChangeSerializer,
        responses={
            200: OpenApiResponse(response=MessageResponseSerializer, description="Password changed successfully"),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="Validation errors")
        }
    )
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

@extend_schema(
    summary="Logout user",
    description="Logout user and blacklist tokens",
    tags=['Authentication'],
    request=LogoutRequestSerializer,
    responses={
        200: OpenApiResponse(response=MessageResponseSerializer, description="Logout successful"),
        400: OpenApiResponse(response=ErrorResponseSerializer, description="Invalid token")
    }
)
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
        
        # Blacklist the refresh token
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

@extend_schema(
    summary="Check username availability",
    description="Check if a username is available for registration",
    tags=['Authentication'],
    parameters=[
        {
            'name': 'username',
            'in': 'query',
            'description': 'Username to check',
            'required': True,
            'schema': {'type': 'string'}
        }
    ],
    responses={
        200: OpenApiResponse(response=AvailabilityResponseSerializer, description="Username availability status"),
        400: OpenApiResponse(response=ErrorResponseSerializer, description="Missing username parameter")
    }
)
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

@extend_schema(
    summary="Check email availability",
    description="Check if an email is available for registration",
    tags=['Authentication'],
    parameters=[
        {
            'name': 'email',
            'in': 'query',
            'description': 'Email to check',
            'required': True,
            'schema': {'type': 'string', 'format': 'email'}
        }
    ],
    responses={
        200: OpenApiResponse(response=AvailabilityResponseSerializer, description="Email availability status"),
        400: OpenApiResponse(response=ErrorResponseSerializer, description="Missing email parameter")
    }
)
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

@extend_schema(
    summary="Refresh access token",
    description="Refresh access token using refresh token",
    tags=['Authentication'],
    request=TokenRefreshRequestSerializer,
    responses={
        200: OpenApiResponse(response=TokenRefreshResponseSerializer, description="Token refreshed successfully"),
        400: OpenApiResponse(response=ErrorResponseSerializer, description="Invalid refresh token")
    }
)
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

@extend_schema(
    summary="Invalidate all tokens (Admin only)",
    description="Invalidate all user tokens system-wide (requires admin privileges)",
    tags=['Authentication'],
    responses={
        200: OpenApiResponse(response=MessageResponseSerializer, description="All tokens invalidated"),
        403: OpenApiResponse(response=ErrorResponseSerializer, description="Admin privileges required"),
        500: OpenApiResponse(response=ErrorResponseSerializer, description="Internal server error")
    }
)
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
