from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from django.utils import timezone
from .models import Category, Poll, Option, Vote
from .serializers import (
    CategorySerializer, PollListSerializer, PollDetailSerializer,
    PollCreateSerializer, PollUpdateSerializer, OptionSerializer
)
from .permissions import IsPollOwnerOrReadOnly, CanVotePermission
from django.db import transaction
from .serializers import VoteSerializer, VoteCastSerializer

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Category ViewSet - Read only"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    
    def get_queryset(self):
        """Filter active categories"""
        queryset = Category.objects.all()
        
        # Filter by active polls only
        if self.request.query_params.get('active_only') == 'true':
            queryset = queryset.filter(polls__is_active=True).distinct()
        
        return queryset.order_by('name')

class PollViewSet(viewsets.ModelViewSet):
    """Poll ViewSet with full CRUD"""
    queryset = Poll.objects.select_related('created_by', 'category').prefetch_related('options')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsPollOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active', 'is_anonymous', 'multiple_choice', 'created_by']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title', 'expires_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return PollListSerializer
        elif self.action == 'create':
            return PollCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return PollUpdateSerializer
        return PollDetailSerializer
    
    def get_queryset(self):
        """Filter queryset based on parameters"""
        queryset = self.queryset
        
        # Filter expired polls
        if self.request.query_params.get('exclude_expired') == 'true':
            now = timezone.now()
            queryset = queryset.filter(
                Q(expires_at__isnull=True) | Q(expires_at__gt=now)
            )
        
        # Filter by current user's polls
        if self.request.query_params.get('my_polls') == 'true':
            if self.request.user.is_authenticated:
                queryset = queryset.filter(created_by=self.request.user)
            else:
                queryset = queryset.none()
        
        # Annotate with vote counts for list view
        if self.action == 'list':
            queryset = queryset.annotate(
                vote_count=Count('votes'),
                unique_voters=Count('votes__user', distinct=True)
            )
        
        return queryset
    
    def perform_create(self, serializer):
        """Set creator when creating poll"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny])
    def results(self, request, pk=None):
        """Get poll results"""
        poll = self.get_object()
        
        # Check if results are finalized
        if poll.results_finalized:
            # Return saved results
            results = poll.results.all().order_by('-vote_count')
            data = []
            for result in results:
                data.append({
                    'option_id': result.option.id,
                    'option_text': result.option.text,
                    'vote_count': result.vote_count,
                    'percentage': float(result.percentage),
                    'rank': result.rank
                })
        else:
            # Calculate live results
            total_votes = poll.get_total_votes()
            options_with_votes = poll.options.annotate(
                vote_count=Count('votes')
            ).order_by('-vote_count', 'order_index')
            
            data = []
            for option in options_with_votes:
                percentage = 0
                if total_votes > 0:
                    percentage = round((option.vote_count / total_votes) * 100, 2)
                
                data.append({
                    'option_id': option.id,
                    'option_text': option.text,
                    'vote_count': option.vote_count,
                    'percentage': percentage,
                    'rank': None  # Will be calculated on finalization
                })
        
        return Response({
            'poll_id': poll.id,
            'poll_title': poll.title,
            'total_votes': poll.get_total_votes(),
            'unique_voters': poll.get_unique_voters(),
            'results_finalized': poll.results_finalized,
            'results': data
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsPollOwnerOrReadOnly])
    def finalize(self, request, pk=None):
        """Finalize poll results"""
        poll = self.get_object()
        
        if poll.results_finalized:
            return Response(
                {'error': 'Poll results are already finalized'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate final results
        total_votes = poll.get_total_votes()
        options_with_votes = poll.options.annotate(
            vote_count=Count('votes')
        ).order_by('-vote_count', 'order_index')
        
        # Create PollResult records
        from .models import PollResult
        results = []
        for rank, option in enumerate(options_with_votes, 1):
            percentage = 0
            if total_votes > 0:
                percentage = round((option.vote_count / total_votes) * 100, 2)
            
            result = PollResult.objects.create(
                poll=poll,
                option=option,
                vote_count=option.vote_count,
                percentage=percentage,
                rank=rank
            )
            results.append(result)
        
        # Mark poll as finalized
        poll.results_finalized = True
        poll.is_active = False  # Stop accepting votes
        poll.save()
        
        return Response({
            'message': 'Poll results finalized successfully',
            'total_votes': total_votes,
            'results_count': len(results)
        })
    
    @action(detail=True, methods=['get'])
    def my_vote(self, request, pk=None):
        """Get current user's vote for this poll"""
        poll = self.get_object()
        
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            vote = Vote.objects.get(poll=poll, user=request.user)
            return Response({
                'has_voted': True,
                'vote_id': vote.id,
                'option_id': vote.option.id,
                'option_text': vote.option.text,
                'voted_at': vote.created_at
            })
        except Vote.DoesNotExist:
            return Response({
                'has_voted': False,
                'vote_id': None,
                'option_id': None,
                'option_text': None,
                'voted_at': None
            })
    
    @action(detail=True, methods=['post'], permission_classes=[CanVotePermission])
    def vote(self, request, pk=None):
        """Cast vote on poll"""
        poll = self.get_object()
        
        # Check if poll accepts votes
        if not poll.can_vote:
            return Response(
                {'error': 'This poll is not accepting votes'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check authentication for non-anonymous polls
        if not poll.is_anonymous and not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required for this poll'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        serializer = VoteCastSerializer(
            data=request.data,
            context={
                'request': request,
                'poll_id': poll.id
            }
        )
        
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    votes = serializer.create_votes()
                    
                    return Response({
                        'message': 'Vote cast successfully',
                        'votes_count': len(votes),
                        'poll_id': poll.id,
                        'voted_options': [
                            {
                                'option_id': vote.option.id,
                                'option_text': vote.option.text
                            }
                            for vote in votes
                        ]
                    }, status=status.HTTP_201_CREATED)
            
            except Exception as e:
                return Response(
                    {'error': f'Failed to cast vote: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'], permission_classes=[permissions.IsAuthenticated])
    def remove_vote(self, request, pk=None):
        """Remove user's vote from poll"""
        poll = self.get_object()
        
        # Check if poll allows vote removal (only if not finalized)
        if poll.results_finalized:
            return Response(
                {'error': 'Cannot remove vote from finalized poll'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Find and delete user's votes
        votes = Vote.objects.filter(poll=poll, user=request.user)
        
        if not votes.exists():
            return Response(
                {'error': 'No vote found for this poll'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        vote_count = votes.count()
        votes.delete()
        
        return Response({
            'message': 'Vote removed successfully',
            'removed_votes': vote_count,
            'poll_id': poll.id
        })
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_votes(self, request):
        """Get current user's votes"""
        votes = Vote.objects.filter(user=request.user).select_related(
            'poll', 'option'
        ).order_by('-created_at')
        
        # Pagination
        page = self.paginate_queryset(votes)
        if page is not None:
            serializer = VoteSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = VoteSerializer(votes, many=True)
        return Response(serializer.data)
