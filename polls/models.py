from django.db import models
from django.utils.text import slugify
from common.models import BaseModel, SlugMixin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

class CategoryManager(models.Manager):
    """Custom manager for Category model"""
    
    def active_categories(self):
        """Get categories that have active polls"""
        return self.filter(polls__is_active=True).distinct()

class Category(BaseModel, SlugMixin):
    """Poll categories for organization"""
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Category name"
    )
    description = models.TextField(
        blank=True,
        help_text="Category description"
    )
    
    objects = CategoryManager()

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_polls_count(self):
        """Get count of active polls in this category"""
        return self.polls.filter(is_active=True).count()

User = get_user_model()

class PollManager(models.Manager):
    """Custom manager for Poll model"""
    
    def active(self):
        """Get active polls"""
        return self.filter(is_active=True)
    
    def expired(self):
        """Get expired polls"""
        now = timezone.now()
        return self.filter(expires_at__lt=now)
    
    def not_expired(self):
        """Get non-expired polls"""
        now = timezone.now()
        return self.filter(
            models.Q(expires_at__isnull=True) | 
            models.Q(expires_at__gt=now)
        )
    
    def with_vote_counts(self):
        """Annotate polls with vote counts"""
        return self.annotate(
            total_votes=models.Count('votes'),
            unique_voters=models.Count('votes__user', distinct=True)
        )

class Poll(BaseModel):
    """Main poll model"""
    title = models.CharField(
        max_length=200,
        help_text="Poll title"
    )
    description = models.TextField(
        blank=True,
        help_text="Optional poll description"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_polls',
        help_text="Poll creator"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='polls',
        help_text="Poll category"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the poll accepts votes"
    )
    is_anonymous = models.BooleanField(
        default=False,
        help_text="Allow anonymous voting"
    )
    multiple_choice = models.BooleanField(
        default=False,
        help_text="Allow multiple option selection"
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the poll expires"
    )
    results_finalized = models.BooleanField(
        default=False,
        help_text="Whether final results have been calculated"
    )
    starts_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the poll becomes active"
    )
    
    auto_finalize = models.BooleanField(
        default=True,
        help_text="Automatically finalize when expired"
    )
    
    objects = PollManager()

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active', 'created_at']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['created_by', 'is_active']),
        ]

    def __str__(self):
        return self.title

    def clean(self):
        """Validate poll data"""
        if self.expires_at and self.expires_at <= timezone.now():
            raise ValidationError("Expiry date must be in the future")
    
    @property
    def is_scheduled(self):
        """Check if poll is scheduled for future"""
        if not self.starts_at:
            return False
        return timezone.now() < self.starts_at
    
    @property
    def can_vote(self):
        """Check if poll can accept votes"""
        now = timezone.now()
        
        # Check if poll is active
        if not self.is_active:
            return False
        
        # Check if poll has started
        if self.starts_at and now < self.starts_at:
            return False
        
        # Check if poll has expired
        if self.expires_at and now > self.expires_at:
            return False
        
        return True
    
    @property
    def status(self):
        """Get poll status"""
        now = timezone.now()
        
        if not self.is_active:
            return 'inactive'
        
        if self.results_finalized:
            return 'finalized'
        
        if self.starts_at and now < self.starts_at:
            return 'scheduled'
        
        if self.expires_at and now > self.expires_at:
            return 'expired'
        
        return 'active'

    @property
    def is_expired(self):
        """Check if poll has expired"""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at

    @property
    def can_vote(self):
        """Check if poll can accept votes"""
        return self.is_active and not self.is_expired

    def get_total_votes(self):
        """Get total vote count"""
        return self.votes.count()

    def get_unique_voters(self):
        """Get unique voter count"""
        return self.votes.values('user').distinct().count()

class Option(BaseModel):
    """Poll option model"""
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name='options',
        help_text="Associated poll"
    )
    text = models.CharField(
        max_length=500,
        help_text="Option text"
    )
    order_index = models.PositiveIntegerField(
        default=0,
        help_text="Display order"
    )

    class Meta:
        ordering = ['order_index', 'created_at']
        unique_together = ['poll', 'order_index']
        indexes = [
            models.Index(fields=['poll', 'order_index']),
        ]

    def __str__(self):
        return f"{self.poll.title} - {self.text[:50]}"

    def get_vote_count(self):
        """Get vote count for this option"""
        return self.votes.count()

    def get_vote_percentage(self, total_votes=None):
        """Get vote percentage for this option"""
        if total_votes is None:
            total_votes = self.poll.get_total_votes()
        
        if total_votes == 0:
            return 0
        
        option_votes = self.get_vote_count()
        return round((option_votes / total_votes) * 100, 2)

class VoteManager(models.Manager):
    """Custom manager for Vote model"""
    
    def for_poll(self, poll):
        """Get votes for a specific poll"""
        return self.filter(poll=poll)
    
    def for_user(self, user):
        """Get votes for a specific user"""
        return self.filter(user=user)
    
    def anonymous(self):
        """Get anonymous votes"""
        return self.filter(user__isnull=True)

class Vote(BaseModel):
    """Vote model"""
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name='votes',
        help_text="Associated poll"
    )
    option = models.ForeignKey(
        Option,
        on_delete=models.CASCADE,
        related_name='votes',
        help_text="Selected option"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='votes',
        null=True,
        blank=True,
        help_text="Voting user (null for anonymous)"
    )
    ip_address = models.GenericIPAddressField(
        help_text="Voter's IP address"
    )
    user_agent = models.TextField(
        blank=True,
        help_text="Voter's user agent"
    )
    
    objects = VoteManager()

    class Meta:
        constraints = [
            # Prevent duplicate votes from registered users
            models.UniqueConstraint(
                fields=['poll', 'user'],
                condition=models.Q(user__isnull=False),
                name='unique_user_poll_vote'
            ),
            # Prevent duplicate anonymous votes from same IP
            models.UniqueConstraint(
                fields=['poll', 'ip_address'],
                condition=models.Q(user__isnull=True),
                name='unique_anonymous_poll_vote'
            ),
        ]
        indexes = [
            models.Index(fields=['poll', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['ip_address', 'created_at']),
        ]

    def __str__(self):
        voter = self.user.username if self.user else f"Anonymous ({self.ip_address})"
        return f"{voter} voted for {self.option.text[:30]} in {self.poll.title}"

    def clean(self):
        """Validate vote data"""
        if not self.poll.can_vote:
            raise ValidationError("This poll is not accepting votes")
        
        if self.option.poll != self.poll:
            raise ValidationError("Option does not belong to this poll")

class PollResult(BaseModel):
    """Finalized poll results"""
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name='results',
        help_text="Associated poll"
    )
    option = models.ForeignKey(
        Option,
        on_delete=models.CASCADE,
        related_name='results',
        help_text="Poll option"
    )
    vote_count = models.PositiveIntegerField(
        default=0,
        help_text="Final vote count"
    )
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Vote percentage"
    )
    rank = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Option ranking by votes"
    )

    class Meta:
        unique_together = ['poll', 'option']
        ordering = ['-vote_count', 'option__order_index']
        indexes = [
            models.Index(fields=['poll', '-vote_count']),
        ]

    def __str__(self):
        return f"{self.poll.title} - {self.option.text}: {self.vote_count} votes"

class VoteSession(BaseModel):
    """Session tracking for anonymous votes"""
    session_key = models.CharField(
        max_length=40,
        unique=True,
        help_text="Session identifier"
    )
    ip_address = models.GenericIPAddressField(
        help_text="Session IP address"
    )
    expires_at = models.DateTimeField(
        help_text="Session expiry"
    )

    class Meta:
        indexes = [
            models.Index(fields=['session_key']),
            models.Index(fields=['ip_address', 'expires_at']),
        ]

    def __str__(self):
        return f"Session {self.session_key} from {self.ip_address}"

    @property
    def is_expired(self):
        """Check if session has expired"""
        return timezone.now() > self.expires_at

    @classmethod
    def cleanup_expired(cls):
        """Remove expired sessions"""
        now = timezone.now()
        return cls.objects.filter(expires_at__lt=now).delete()
