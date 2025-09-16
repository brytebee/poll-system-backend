# authentication/views.py
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import login
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer,
    UserProfileSerializer, UserUpdateSerializer,
    PasswordChangeSerializer
)
from .models import CustomUser

class UserRegistrationView(APIView):
    """User registration endpoint"""
    permission_classes = [permissions.AllowAny]
    
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
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return UserUpdateSerializer
        return UserProfileSerializer

class PasswordChangeView(APIView):
    """Password change endpoint"""
    permission_classes = [permissions.IsAuthenticated]
    
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

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def logout_view(request):
    """Logout endpoint - works with or without authentication"""
    try:
        refresh_token = request.data.get('refresh_token')
        print("=====hi there=====")
        print({refresh_token})
        
        if not refresh_token:
            return Response({
                'error': 'Refresh token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        token = RefreshToken(refresh_token)
        token.blacklist()
        
        return Response({
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Invalid token'
        }, status=status.HTTP_400_BAD_REQUEST)

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
