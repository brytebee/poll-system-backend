from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample, OpenApiParameter, OpenApiTypes
from rest_framework import status

# Registration examples
auth_register_example = [
    OpenApiExample(
        'User Registration',
        summary='Register new user',
        description='Create a new user account with automatic login',
        value={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "first_name": "John",
            "last_name": "Doe"
        },
        request_only=True
    ),
    OpenApiExample(
        'Registration Success Response',
        summary='Successful registration',
        description='User registered successfully with tokens',
        value={
            "message": "Registration successful",
            "user": {
                "id": "123e4567-e89b-12d3-a456-426614174001",
                "username": "newuser",
                "email": "newuser@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "display_name": "John Doe",
                "is_active": True,
                "date_joined": "2024-01-15T10:30:00Z"
            },
            "tokens": {
                "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
            }
        },
        response_only=True,
        status_codes=[status.HTTP_201_CREATED]
    )
]

# Login examples
auth_login_example = [
    OpenApiExample(
        'User Login',
        summary='Login user',
        description='Authenticate user and get tokens',
        value={
            "username": "testuser",
            "password": "SecurePass123!"
        },
        request_only=True
    ),
    OpenApiExample(
        'Login Success Response',
        summary='Successful login',
        description='User authenticated with tokens and profile data',
        value={
            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "user": {
                "id": "123e4567-e89b-12d3-a456-426614174001",
                "username": "testuser",
                "email": "testuser@example.com",
                "first_name": "Test",
                "last_name": "User",
                "display_name": "Test User",
                "is_active": True,
                "date_joined": "2024-01-15T10:30:00Z"
            },
            "message": "Login successful"
        },
        response_only=True,
        status_codes=[status.HTTP_200_OK]
    )
]

# Profile examples
profile_update_example = [
    OpenApiExample(
        'Profile Update',
        summary='Update user profile',
        description='Update user profile information',
        value={
            "first_name": "Updated Name",
            "last_name": "Updated Surname",
            "email": "updated@example.com"
        },
        request_only=True
    )
]

# Password change examples
password_change_example = [
    OpenApiExample(
        'Change Password',
        summary='Change user password',
        description='Change current user password',
        value={
            "old_password": "OldPass123!",
            "new_password": "NewSecurePass123!",
            "new_password_confirm": "NewSecurePass123!"
        },
        request_only=True
    )
]

# Logout examples
logout_example = [
    OpenApiExample(
        'Logout Request',
        summary='Logout user',
        description='Invalidate refresh and access tokens',
        value={
            "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
        },
        request_only=True
    )
]

# schema decorators for views
register_user_schema = extend_schema(
    summary="Register User",
    description="Register a new user account",
    examples=auth_register_example,
    tags=['Authentication']
)

login_user_schema = extend_schema(
    summary="Login User", 
    description="Authenticate user and receive access/refresh tokens",
    examples=auth_login_example,
    tags=['Authentication']
)

user_profile_schema = extend_schema_view(
    get=extend_schema(
        summary="Get User Profile",
        description="Retrieve current user's profile information",
        tags=['Authentication']
    ),
    put=extend_schema(
        summary="Update User Profile",
        description="Update current user's profile information",
        examples=profile_update_example,
        tags=['Authentication']
    ),
    patch=extend_schema(
        summary="Partially Update User Profile",
        description="Partially update current user's profile information",
        examples=profile_update_example,
        tags=['Authentication']
    )
)

change_password_schema = extend_schema(
    summary="Change Password",
    description="Change current user's password",
    examples=password_change_example,
    tags=['Authentication']
)

logout_schema = extend_schema(
    summary="Logout User",
    description="Logout user and invalidate tokens immediately",
    examples=logout_example,
    tags=['Authentication']
)

check_username_schema = extend_schema(
    summary="Check Username Availability",
    description="Check if a username is available for registration",
    parameters=[
        OpenApiParameter(
            name='username',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Username to check',
            required=True
        )
    ],
    tags=['Authentication']
)

check_email_schema = extend_schema(
    summary="Check Email Availability",
    description="Check if an email is available for registration",
    parameters=[
        OpenApiParameter(
            name='email',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Email to check',
            required=True
        )
    ],
    tags=['Authentication']
)

refresh_token_schema = extend_schema(
    summary="Refresh Access Token",
    description="Refresh access token using refresh token",
    tags=['Authentication']
)

invalidate_token_schema = extend_schema(
    summary="Invalidate All Tokens (Admin)",
    description="Admin endpoint to invalidate all user tokens system-wide",
    tags=['Authentication']
)
