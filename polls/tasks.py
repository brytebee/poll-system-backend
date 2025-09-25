# polls/tasks.py
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Count, Q
from celery import shared_task
from .models import Poll, VoteSession, Category
from .services.results_service import PollResultsService

@shared_task
def finalize_expired_polls():
    """Finalize polls that have expired"""
    now = timezone.now()
    expired_polls = Poll.objects.filter(
        expires_at__lt=now,
        results_finalized=False,
        is_active=True
    )
    
    finalized_count = 0
    for poll in expired_polls:
        success, message = PollResultsService.finalize_poll_results(poll)
        if success:
            finalized_count += 1
    
    return f"Finalized {finalized_count} expired polls"

@shared_task
def cleanup_expired_sessions():
    """Clean up expired vote sessions"""
    count, _ = VoteSession.cleanup_expired()
    return f"Cleaned up {count} expired sessions"

@shared_task
def update_popular_polls_cache():
    """Update popular polls cache"""
    from django.db.models import Count
    from .services.cache_service import PollCacheService
    
    popular_polls = Poll.objects.annotate(
        vote_count=Count('votes')
    ).filter(vote_count__gt=0).order_by('-vote_count')[:10]
    
    data = []
    for poll in popular_polls:
        data.append({
            'id': str(poll.id),
            'title': poll.title,
            'vote_count': poll.vote_count,
            'created_by': poll.created_by.display_name,
            'category': poll.category.name if poll.category else None,
            'created_at': poll.created_at.isoformat()
        })
    
    PollCacheService.cache_popular_polls(data)
    return f"Updated cache with {len(data)} popular polls"

@shared_task
def update_poll_caches():
    """Update poll-related caches in background"""
    
    # Update category poll counts
    categories = Category.objects.annotate(
        polls_count=Count('polls', filter=Q(polls__is_active=True))
    )
    
    for category in categories:
        cache_key = f"category_{category.id}_polls_count"
        cache.set(cache_key, category.polls_count, timeout=3600)  # 1 hour
    
    # Update active polls total votes
    polls = Poll.objects.filter(is_active=True).annotate(
        total_votes=Count('votes')
    )
    
    for poll in polls:
        cache_key = f"poll_{poll.id}_total_votes"
        cache.set(cache_key, poll.total_votes, timeout=1800)  # 30 minutes
    
    return f"Updated caches for {categories.count()} categories and {polls.count()} polls"

@shared_task
def finalize_expired_polls():
    """Finalize results for expired polls"""
    from django.utils import timezone
    
    expired_polls = Poll.objects.filter(
        expires_at__lte=timezone.now(),
        results_finalized=False,
        is_active=True
    )
    
    for poll in expired_polls:
        # Calculate and store final results
        poll.finalize_results()
        
        # Clear real-time caches
        cache.delete(f"poll_detail_{poll.id}")
        cache.delete(f"poll_{poll.id}_total_votes")
    
    return f"Finalized {expired_polls.count()} expired polls"
