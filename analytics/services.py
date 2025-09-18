from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from collections import defaultdict
from polls.models import Poll, Vote, Category
from django.contrib.auth import get_user_model

User = get_user_model()

class AnalyticsService:
    """Service for generating analytics data"""
    
    @staticmethod
    def get_poll_analytics(poll):
        """Get detailed analytics for a specific poll"""
        votes = Vote.objects.filter(poll=poll)
        total_votes = votes.count()
        unique_voters = votes.values('user').distinct().count()
        
        # Votes per day
        votes_per_day = []
        if votes.exists():
            first_vote = votes.earliest('created_at').created_at.date()
            last_vote = votes.latest('created_at').created_at.date()
            
            current_date = first_vote
            while current_date <= last_vote:
                day_votes = votes.filter(created_at__date=current_date).count()
                votes_per_day.append({
                    'date': current_date.isoformat(),
                    'votes': day_votes
                })
                current_date += timedelta(days=1)
        
        # Demographics (if users available)
        demographics = {
            'registered_users': votes.filter(user__isnull=False).count(),
            'anonymous_users': votes.filter(user__isnull=True).count()
        }
        
        # Engagement metrics
        poll_age_hours = (timezone.now() - poll.created_at).total_seconds() / 3600
        engagement_rate = total_votes / max(poll_age_hours, 1)
        
        # Completion rate (users who voted vs poll views - approximation)
        completion_rate = min(unique_voters / max(total_votes, 1), 1.0) * 100
        
        return {
            'poll_id': poll.id,
            'title': poll.title,
            'total_votes': total_votes,
            'unique_voters': unique_voters,
            'votes_per_day': votes_per_day,
            'demographics': demographics,
            'engagement_rate': round(engagement_rate, 2),
            'completion_rate': round(completion_rate, 2)
        }
    
    @staticmethod
    def get_user_analytics(user):
        """Get detailed analytics for a specific user"""
        polls_created = Poll.objects.filter(created_by=user).count()
        votes_cast = Vote.objects.filter(user=user).count()
        
        # Engagement score calculation
        total_votes_on_user_polls = Vote.objects.filter(poll__created_by=user).count()
        engagement_score = (votes_cast * 0.3 + polls_created * 0.4 + total_votes_on_user_polls * 0.3)
        
        # Favorite categories
        favorite_categories = list(
            Category.objects.filter(
                Q(polls__created_by=user) | Q(polls__votes__user=user)
            ).annotate(
                interaction_count=Count('polls__votes', filter=Q(polls__votes__user=user)) + 
                                Count('polls', filter=Q(polls__created_by=user))
            ).order_by('-interaction_count')[:5].values_list('name', flat=True)
        )
        
        # Activity timeline (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        activity_timeline = []
        
        polls_created_timeline = Poll.objects.filter(
            created_by=user,
            created_at__gte=thirty_days_ago
        ).extra({'day': 'date(created_at)'}).values('day').annotate(count=Count('id'))
        
        votes_cast_timeline = Vote.objects.filter(
            user=user,
            created_at__gte=thirty_days_ago
        ).extra({'day': 'date(created_at)'}).values('day').annotate(count=Count('id'))
        
        # Combine timelines
        activity_dict = defaultdict(lambda: {'polls_created': 0, 'votes_cast': 0})
        
        for item in polls_created_timeline:
            activity_dict[item['day']]['polls_created'] = item['count']
        
        for item in votes_cast_timeline:
            activity_dict[item['day']]['votes_cast'] = item['count']
        
        for day, data in activity_dict.items():
            activity_timeline.append({
                'date': day,
                'polls_created': data['polls_created'],
                'votes_cast': data['votes_cast']
            })
        
        activity_timeline.sort(key=lambda x: x['date'])
        
        return {
            'user_id': user.id,
            'username': user.username,
            'polls_created': polls_created,
            'votes_cast': votes_cast,
            'engagement_score': round(engagement_score, 2),
            'favorite_categories': favorite_categories,
            'activity_timeline': activity_timeline
        }
    
    @staticmethod
    def get_system_health_metrics():
        """Get system health and performance metrics"""
        from django.db import connection
        
        # Database metrics
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM django_session")
            active_sessions = cursor.fetchone()[0]
        
        # Performance metrics
        total_polls = Poll.objects.count()
        active_polls = Poll.objects.filter(is_active=True).count()
        total_votes = Vote.objects.count()
        total_users = User.objects.count()
        
        # Recent activity (last 24 hours)
        day_ago = timezone.now() - timedelta(days=1)
        recent_polls = Poll.objects.filter(created_at__gte=day_ago).count()
        recent_votes = Vote.objects.filter(created_at__gte=day_ago).count()
        recent_users = User.objects.filter(date_joined__gte=day_ago).count()
        
        # System health indicators
        avg_votes_per_poll = Vote.objects.count() / max(Poll.objects.count(), 1)
        polls_with_votes_ratio = Poll.objects.filter(votes__isnull=False).distinct().count() / max(total_polls, 1)
        
        return {
            'database': {
                'total_polls': total_polls,
                'active_polls': active_polls,
                'total_votes': total_votes,
                'total_users': total_users,
                'active_sessions': active_sessions
            },
            'activity': {
                'polls_last_24h': recent_polls,
                'votes_last_24h': recent_votes,
                'users_last_24h': recent_users
            },
            'performance': {
                'avg_votes_per_poll': round(avg_votes_per_poll, 2),
                'polls_with_votes_ratio': round(polls_with_votes_ratio * 100, 2),
                'system_uptime': timezone.now().isoformat()
            }
        }
    