# authentication/models.py
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

def user_avatar_path(instance, filename):
    """Generate file path for user avatars"""
    return f'avatars/{instance.username}/{filename}'

class CustomUser(AbstractUser):
    """Custom user model with UUID and additional fields"""
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        help_text="Required. Must be a valid email address."
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
        help_text="Tell us about yourself"
    )
    avatar = models.ImageField(
        upload_to=user_avatar_path,
        blank=True,
        null=True,
        help_text="Profile picture"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Override username to allow longer usernames
    username = models.CharField(
        max_length=150,
        unique=True,
        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
    )

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        db_table = 'auth_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def display_name(self):
        """Get display name (full name or username)"""
        return self.full_name if self.full_name else self.username

    def get_polls_created_count(self):
        """Count of polls created by user"""
        return self.created_polls.filter(is_active=True).count()

    def get_votes_cast_count(self):
        """Count of votes cast by user"""
        return self.votes.count()
