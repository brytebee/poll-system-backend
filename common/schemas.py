from drf_spectacular.utils import OpenApiExample
from rest_framework import status

# Common error responses
error_responses = {
    'validation_error': OpenApiExample(
        'Validation Error',
        summary='Validation failed',
        description='Request data validation failed',
        value={
            "field_name": ["This field is required."],
            "another_field": ["This field must be unique."]
        },
        response_only=True,
        status_codes=[status.HTTP_400_BAD_REQUEST]
    ),
    'authentication_error': OpenApiExample(
        'Authentication Error',
        summary='Authentication failed',
        description='Invalid or missing authentication credentials',
        value={
            "detail": "Authentication credentials were not provided."
        },
        response_only=True,
        status_codes=[status.HTTP_401_UNAUTHORIZED]
    ),
    'permission_error': OpenApiExample(
        'Permission Error',
        summary='Permission denied',
        description='User does not have permission to perform this action',
        value={
            "detail": "You do not have permission to perform this action."
        },
        response_only=True,
        status_codes=[status.HTTP_403_FORBIDDEN]
    ),
    'not_found_error': OpenApiExample(
        'Not Found Error',
        summary='Resource not found',
        description='The requested resource was not found',
        value={
            "detail": "Not found."
        },
        response_only=True,
        status_codes=[status.HTTP_404_NOT_FOUND]
    )
}
