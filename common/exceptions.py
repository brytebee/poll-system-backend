from rest_framework import status
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class PollSystemException(Exception):
    """Base exception for poll system"""
    default_message = "An error occurred"
    default_code = "error"
    
    def __init__(self, message=None, code=None):
        self.message = message or self.default_message
        self.code = code or self.default_code
        super().__init__(self.message)

class VotingException(PollSystemException):
    """Exception for voting-related errors"""
    default_message = "Voting error occurred"
    default_code = "voting_error"

class PollNotFoundException(PollSystemException):
    """Exception when poll is not found"""
    default_message = "Poll not found"
    default_code = "poll_not_found"

class DuplicateVoteException(VotingException):
    """Exception for duplicate voting attempts"""
    default_message = "You have already voted on this poll"
    default_code = "duplicate_vote"

class PollExpiredException(VotingException):
    """Exception when trying to vote on expired poll"""
    default_message = "This poll has expired"
    default_code = "poll_expired"

class PollInactiveException(VotingException):
    """Exception when trying to vote on inactive poll"""
    default_message = "This poll is not active"
    default_code = "poll_inactive"

class InvalidOptionException(VotingException):
    """Exception for invalid option selection"""
    default_message = "Invalid option selected"
    default_code = "invalid_option"

class AuthenticationFailedException(PollSystemException):
    """Exception for authentication failures"""
    default_message = "Authentication failed"
    default_code = "auth_failed"

class PermissionDeniedException(PollSystemException):
    """Exception for permission denied"""
    default_message = "Permission denied"
    default_code = "permission_denied"

class RateLimitExceededException(PollSystemException):
    """Exception for rate limiting"""
    default_message = "Rate limit exceeded"
    default_code = "rate_limit_exceeded"

class ValidationException(PollSystemException):
    """Exception for validation errors"""
    default_message = "Validation failed"
    default_code = "validation_error"
    
    def __init__(self, errors, message=None, code=None):
        self.errors = errors
        super().__init__(message, code)

def custom_exception_handler(exc, context):
    """Custom exception handler for API errors"""
    
    # Get the standard error response
    response = drf_exception_handler(exc, context)
    
    if response is not None:
        custom_response_data = {
            'error': True,
            'message': 'An error occurred',
            'details': response.data,
            'status_code': response.status_code
        }
        
        # Handle different exception types
        if hasattr(exc, 'default_code'):
            custom_response_data['code'] = exc.default_code
        
        if hasattr(exc, 'message'):
            custom_response_data['message'] = exc.message
        
        # Log the error
        logger.error(
            f"API Error: {exc.__class__.__name__} - {custom_response_data['message']} "
            f"- Status: {response.status_code} - Path: {context.get('request', {}).path if context else 'Unknown'}"
        )
        
        response.data = custom_response_data
    
    else:
        # Handle unexpected exceptions
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        
        response = Response({
            'error': True,
            'message': 'Internal server error',
            'details': str(exc) if settings.DEBUG else 'An unexpected error occurred',
            'status_code': 500
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return response