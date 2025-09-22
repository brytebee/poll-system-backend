# polls/validators.py
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_poll_title(value: str):
    """
    Validate Poll title:
    - Must not be empty or only whitespace
    - Length between 5 and 200 characters
    - No excessive punctuation or special characters
    """
    if not value or not value.strip():
        raise ValidationError(_("Poll title cannot be empty."))

    if len(value.strip()) < 5:
        raise ValidationError(_("Poll title must be at least 5 characters long."))

    if len(value.strip()) > 200:
        raise ValidationError(_("Poll title cannot exceed 200 characters."))

    # Restrict too many special characters
    if not re.match(r"^[\w\s\-\?\!\.,'\"()]+$", value):
        raise ValidationError(_("Poll title contains invalid characters."))


def validate_option_text(value: str):
    """
    Validate Option text:
    - Must not be empty or only whitespace
    - Length between 1 and 500 characters
    - Should not duplicate generic placeholders (e.g., "Option 1")
    """
    if not value or not value.strip():
        raise ValidationError(_("Option text cannot be empty."))

    if len(value.strip()) > 500:
        raise ValidationError(_("Option text cannot exceed 500 characters."))

    # Prevent generic placeholders
    generic_patterns = [
        r"^option\s*\d+$",   # "Option 1"
        r"^choice\s*\d+$",   # "Choice 2"
        r"^answer\s*\d+$",   # "Answer 3"
    ]
    for pattern in generic_patterns:
        if re.match(pattern, value.strip(), flags=re.IGNORECASE):
            raise ValidationError(_("Option text is too generic, please provide a meaningful option."))

    # Restrict unsupported characters
    if not re.match(r"^[\w\s\-\?\!\.,'\"()]+$", value):
        raise ValidationError(_("Option text contains invalid characters."))
