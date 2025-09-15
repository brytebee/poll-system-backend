import uuid
from django.db import models
from django.conf import settings

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Category(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

class Poll(BaseModel):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='polls')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='polls')
    is_active = models.BooleanField(default=True)
    is_anonymous = models.BooleanField(default=False)
    multiple_choice = models.BooleanField(default=False)
    expires_at = models.DateTimeField(blank=True, null=True)
    results_finalized = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class Option(BaseModel):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=500)
    order_index = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.poll.title} - {self.text}"

    class Meta:
        ordering = ['order_index']

class Vote(BaseModel):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='votes')
    option = models.ForeignKey(Option, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='votes', null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['poll', 'user'],
                name='unique_user_poll_vote',
                condition=models.Q(user__isnull=False)
            ),
        ]

class VoteSession(BaseModel):
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    expires_at = models.DateTimeField()

class PollResult(BaseModel):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='results')
    option = models.ForeignKey(Option, on_delete=models.CASCADE, related_name='results')
    vote_count = models.IntegerField(default=0)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    rank = models.IntegerField(blank=True, null=True)

    class Meta:
        unique_together = ['poll', 'option']
