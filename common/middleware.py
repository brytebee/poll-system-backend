import logging
from django.utils.deprecation import MiddlewareMixin
from polls.models import Vote, PollResult
from polls.services.cache_service import PollCacheService
from django.db.models import Count
from django.db import transaction

logger = logging.getLogger(__name__)

class SecurityHeadersMiddleware(MiddlewareMixin):
    """Add security headers to"""    
    
    @staticmethod
    def _calculate_live_results(poll):
        """Calculate live results"""
        # Optimized query to get vote counts per option
        options_with_votes = poll.options.annotate(
            vote_count=Count('votes')
        ).order_by('-vote_count', 'order_index')
        
        total_votes = sum(option.vote_count for option in options_with_votes)
        unique_voters = Vote.objects.filter(poll=poll).values('user').distinct().count()
        
        data = []
        for option in options_with_votes:
            percentage = 0
            if total_votes > 0:
                percentage = round((option.vote_count / total_votes) * 100, 2)
            
            data.append({
                'option_id': str(option.id),
                'option_text': option.text,
                'vote_count': option.vote_count,
                'percentage': percentage,
                'rank': None
            })
        
        return {
            'poll_id': str(poll.id),
            'poll_title': poll.title,
            'total_votes': total_votes,
            'unique_voters': unique_voters,
            'results_finalized': False,
            'results': data
        }
    
    @staticmethod
    def finalize_poll_results(poll):
        """Finalize poll results and save to database"""
        if poll.results_finalized:
            return False, "Results already finalized"
        
        with transaction.atomic():
            # Calculate final results
            options_with_votes = poll.options.annotate(
                vote_count=Count('votes')
            ).order_by('-vote_count', 'order_index')
            
            total_votes = sum(option.vote_count for option in options_with_votes)
            
            # Create PollResult records
            for rank, option in enumerate(options_with_votes, 1):
                percentage = 0
                if total_votes > 0:
                    percentage = round((option.vote_count / total_votes) * 100, 2)
                
                PollResult.objects.create(
                    poll=poll,
                    option=option,
                    vote_count=option.vote_count,
                    percentage=percentage,
                    rank=rank
                )
            
            # Mark as finalized
            poll.results_finalized = True
            poll.is_active = False
            poll.save()
            
            # Invalidate cache
            PollCacheService.invalidate_poll_cache(poll.id)
        
        return True, f"Results finalized with {total_votes} votes"
    
    @staticmethod
    def invalidate_poll_results_cache(poll_id):
        """Invalidate cache when poll data changes"""
        PollCacheService.invalidate_poll_cache(poll_id)
