# polls/tasks.py
from poll_system.celery import shared_task
from django.utils import timezone
from .models import Poll, VoteSession
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
