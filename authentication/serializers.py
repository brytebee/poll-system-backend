from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import CustomUser

class UserRegistrationSerializer(serializers.ModelSerializer):
    """User registration serializer"""
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = (
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'bio'
        )
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, attrs):
        """Validate password confirmation"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        """Create new user"""
        validated_data.pop('password_confirm')
        user = CustomUser.objects.create_user(**validated_data)
        return user

class UserLoginSerializer(serializers.Serializer):
    """User login serializer"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Validate login credentials"""
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(
                request=self.context.get('request'),
                username=username,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError(
                    'Invalid username or password'
                )
            
            if not user.is_active:
                raise serializers.ValidationError(
                    'Account is disabled'
                )
            
            attrs['user'] = user
            return attrs
        
        raise serializers.ValidationError(
            'Must include username and password'
        )

class UserProfileSerializer(serializers.ModelSerializer):
    """User profile serializer"""
    full_name = serializers.ReadOnlyField()
    display_name = serializers.ReadOnlyField()
    polls_created_count = serializers.ReadOnlyField(source='get_polls_created_count')
    votes_cast_count = serializers.ReadOnlyField(source='get_votes_cast_count')

    class Meta:
        model = CustomUser
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'bio', 'avatar', 'full_name', 'display_name',
            'date_joined', 'last_login', 'polls_created_count',
            'votes_cast_count'
        )
        read_only_fields = ('id', 'username', 'date_joined', 'last_login')

class UserUpdateSerializer(serializers.ModelSerializer):
    """User profile update serializer"""
    
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'bio', 'avatar')

class PasswordChangeSerializer(serializers.Serializer):
    """Password change serializer"""
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        """Validate old password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect')
        return value

    def validate(self, attrs):
        """Validate password confirmation"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs

    def save(self):
        """Update user password"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
