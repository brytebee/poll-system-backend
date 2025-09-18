from django.db.models import Count
from django.db import transaction
from ..models import Vote, PollResult
from .cache_service import PollCacheService

class PollResultsService:
    """Service for calculating and managing poll results"""

    @staticmethod
    def get_poll_results(poll, use_cache=True):
        """Get poll results (cached or calculated)"""
        if use_cache:
            cached_results = PollCacheService.get_cached_poll_results(poll.id)
            if cached_results:
                return cached_results
        
        if poll.results_finalized:
            results = PollResultsService._get_finalized_results(poll)
        else:
            results = PollResultsService._calculate_live_results(poll)
        
        # Cache the results
        if use_cache:
            PollCacheService.cache_poll_results(poll, results)
        
        return results

    @staticmethod
    def _get_finalized_results(poll):
        """Get finalized results from database"""
        results = poll.results.select_related('option').order_by('rank')
        
        data = []
        for result in results:
            data.append({
                'option_id': str(result.option.id),
                'option_text': result.option.text,
                'vote_count': result.vote_count,
                'percentage': float(result.percentage),
                'rank': result.rank
            })

        return {
            'poll_id': str(poll.id),
            'poll_title': poll.title,
            'total_votes': sum(r['vote_count'] for r in data),
            'unique_voters': poll.get_unique_voters(),
            'results_finalized': True,
            'results': data
        }

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
