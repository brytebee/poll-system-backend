# security/validators.py
from django.core.exceptions import ValidationError
import re

class InputValidator:
    """Centralized input validation"""
    
    @staticmethod
    def validate_text_input(value, min_length=1, max_length=500, allow_html=False):
        """Validate text input"""
        if not value or len(value.strip()) < min_length:
            raise ValidationError(f"Text must be at least {min_length} characters")
        
        if len(value) > max_length:
            raise ValidationError(f"Text cannot exceed {max_length} characters")
        
        if not allow_html and re.search(r'<[^>]*>', value):
            raise ValidationError("HTML tags are not allowed")
        
        return value.strip()

    @staticmethod
    def validate_email(email):
        """Enhanced email validation"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError("Invalid email format")
        return email.lower()
