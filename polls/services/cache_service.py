from django.core.cache import cache
from django.conf import settings

class PollCacheService:
    """Service for caching poll-related data"""
    
    @staticmethod
    def get_poll_results_cache_key(poll_id):
        return f"poll_results_{poll_id}"
    
    @staticmethod
    def get_poll_stats_cache_key(poll_id):
        return f"poll_stats_{poll_id}"
    
    @staticmethod
    def get_popular_polls_cache_key():
        return "popular_polls"
    
    @staticmethod
    def cache_poll_results(poll, results_data):
        """Cache poll results"""
        cache_key = PollCacheService.get_poll_results_cache_key(poll.id)
        ttl = settings.FINALIZED_RESULTS_CACHE_TTL if poll.results_finalized else settings.POLL_RESULTS_CACHE_TTL
        cache.set(cache_key, results_data, ttl)
    
    @staticmethod
    def get_cached_poll_results(poll_id):
        """Get cached poll results"""
        cache_key = PollCacheService.get_poll_results_cache_key(poll_id)
        return cache.get(cache_key)
    
    @staticmethod
    def invalidate_poll_cache(poll_id):
        """Invalidate all cache for a specific poll"""
        keys_to_delete = [
            PollCacheService.get_poll_results_cache_key(poll_id),
            PollCacheService.get_poll_stats_cache_key(poll_id)
        ]
        cache.delete_many(keys_to_delete)
        # Also invalidate popular polls cache
        cache.delete(PollCacheService.get_popular_polls_cache_key())
    
    @staticmethod
    def cache_popular_polls(data):
        """Cache popular polls"""
        cache_key = PollCacheService.get_popular_polls_cache_key()
        cache.set(cache_key, data, settings.CACHE_TTL)
    
    @staticmethod
    def get_cached_popular_polls():
        """Get cached popular polls"""
        cache_key = PollCacheService.get_popular_polls_cache_key()
        return cache.get(cache_key)
