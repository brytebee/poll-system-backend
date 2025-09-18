from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Vote, Poll
from .services.cache_service import PollCacheService
from .tasks import update_popular_polls_cache

@receiver(post_save, sender=Vote)
def invalidate_poll_cache_on_vote(sender, instance, created, **kwargs):
    """Invalidate poll cache when a new vote is cast"""
    if created:
        PollCacheService.invalidate_poll_cache(instance.poll.id)
        # Trigger popular polls cache update
        update_popular_polls_cache.delay()

@receiver(post_delete, sender=Vote)
def invalidate_poll_cache_on_vote_delete(sender, instance, **kwargs):
    """Invalidate poll cache when a vote is deleted"""
    PollCacheService.invalidate_poll_cache(instance.poll.id)

@receiver(post_save, sender=Poll)
def handle_poll_changes(sender, instance, created, **kwargs):
    """Handle poll creation/updates"""
    if created:
        # New poll created - update popular polls cache
        update_popular_polls_cache.delay()
    else:
        # Existing poll updated - invalidate its cache
        PollCacheService.invalidate_poll_cache(instance.id)
    