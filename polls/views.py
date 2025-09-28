# polls/views.py
from django.db.models import Count, Prefetch, Q, F
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import Poll, Option, Vote, Category
from .serializers import (
    PollListSerializer, PollDetailSerializer, PollCreateSerializer,
    VoteCastSerializer, CategorySerializer
)
from .permissions import IsPollOwnerOrReadOnly, CanVotePermission

class PollViewSet(viewsets.ModelViewSet):
    """Optimized Poll ViewSet with efficient queries"""
    
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsPollOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active', 'created_by']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'title']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PollListSerializer
        elif self.action == 'create':
            return PollCreateSerializer
        return PollDetailSerializer
    
    def get_permissions(self):
        """Get permissions based on action"""
        if self.action == 'vote':
            return [CanVotePermission()]
        return super().get_permissions()
    
    def get_queryset(self):
        """Optimized queryset based on action"""
        # For list and retrieve, we want active polls by default
        # For create/update/delete, we want all polls owned by user
        if self.action in ['update', 'partial_update', 'destroy']:
            if self.request.user.is_authenticated:
                return Poll.objects.filter(created_by=self.request.user)
            return Poll.objects.none()
        
        base_queryset = Poll.objects.all()
        
        if self.action == 'list':
            # Optimized list view with minimal data
            queryset = base_queryset.select_related(
                'created_by', 'category'
            ).annotate(
                total_votes=Count('votes'),
                options_count=Count('options'),
                unique_voters=Count('votes__user', distinct=True) + 
                            Count('votes__ip_address', 
                                 filter=Q(votes__user__isnull=True), 
                                 distinct=True)
            )
            
            # Apply default filter for active polls if not explicitly filtered
            if not self.request.GET.get('is_active'):
                queryset = queryset.filter(is_active=True)
            
            return queryset
        
        elif self.action == 'retrieve':
            # Detailed view with all related data
            user = getattr(self.request, 'user', None)
            
            queryset = base_queryset.select_related(
                'created_by', 'category'
            ).prefetch_related(
                Prefetch(
                    'options',
                    queryset=Option.objects.annotate(
                        vote_count=Count('votes')
                    ).order_by('order_index')
                )
            ).annotate(
                total_votes_count=Count('votes'),
                unique_voters_count=Count('votes__user', distinct=True) + 
                            Count('votes__ip_address', 
                                 filter=Q(votes__user__isnull=True), 
                                 distinct=True)
            )
            
            # Add user's votes if authenticated
            if user and user.is_authenticated:
                queryset = queryset.prefetch_related(
                    Prefetch(
                        'votes',
                        queryset=Vote.objects.filter(user=user),
                        to_attr='user_votes'
                    )
                )
            
            return queryset
        
        return base_queryset
    
    def list(self, request, *args, **kwargs):
        """List view with optional caching for anonymous users"""
        # Only cache for anonymous users to avoid permission issues
        if not request.user.is_authenticated:
            cache_key = f"polls_list_{hash(str(sorted(request.GET.items())))}"
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)
            
            response = super().list(request, *args, **kwargs)
            if response.status_code == 200:
                cache.set(cache_key, response.data, timeout=300)  # 5 minutes
            return response
        
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve with caching for poll details"""
        instance = self.get_object()
        
        # Cache poll details for anonymous users
        if not request.user.is_authenticated:
            cache_key = f"poll_detail_{instance.id}"
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)
            
            serializer = self.get_serializer(instance)
            cache.set(cache_key, serializer.data, timeout=300)  # 5 minutes
            return Response(serializer.data)
        
        # No caching for authenticated users (personalized data)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """Create poll with proper error handling"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            poll = serializer.save()
            # Return detailed poll data
            detail_serializer = PollDetailSerializer(poll, context={'request': request})
            return Response(detail_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        """Update poll with cache invalidation"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            poll = serializer.save()
            # Clear caches
            cache.delete(f"poll_detail_{poll.id}")
            
            # Return updated poll data
            detail_serializer = PollDetailSerializer(poll, context={'request': request})
            return Response(detail_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[CanVotePermission])
    def vote(self, request, pk=None):
        """Optimized voting endpoint"""
        poll = self.get_object()
        
        serializer = VoteCastSerializer(
            data=request.data,
            context={'request': request, 'poll': poll}
        )
        
        if serializer.is_valid():
            votes = serializer.create_votes()
            
            # Return updated poll data
            updated_poll = Poll.objects.select_related('category', 'created_by').annotate(
                total_votes_count=Count('votes'),
                unique_voters_count=Count('votes__user', distinct=True) + 
                            Count('votes__ip_address', 
                                 filter=Q(votes__user__isnull=True), 
                                 distinct=True)
            ).prefetch_related(
                Prefetch(
                    'options',
                    queryset=Option.objects.annotate(
                        vote_count=Count('votes')
                    ).order_by('order_index')
                )
            ).get(id=poll.id)
            
            # Clear caches
            cache.delete(f"poll_detail_{poll.id}")
            
            return Response({
                'message': f'Vote{"s" if len(votes) > 1 else ""} cast successfully',
                'votes_count': len(votes),
                'poll': PollDetailSerializer(updated_poll, context={'request': request}).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        """Get poll results"""
        poll = self.get_object()
        
        # Use cached results for better performance
        cache_key = f"poll_results_{poll.id}"
        cached_results = cache.get(cache_key)
        
        if cached_results:
            return Response(cached_results)
        
        # Get poll with vote counts
        poll_with_counts = Poll.objects.select_related('category', 'created_by').annotate(
            total_votes_count=Count('votes'),
            unique_voters_count=Count('votes__user', distinct=True) + 
                        Count('votes__ip_address', 
                             filter=Q(votes__user__isnull=True), 
                             distinct=True)
        ).prefetch_related(
            Prefetch(
                'options',
                queryset=Option.objects.annotate(
                    vote_count=Count('votes')
                ).order_by('order_index')
            )
        ).get(id=poll.id)
        
        serializer = PollDetailSerializer(poll_with_counts, context={'request': request})
        results_data = serializer.data
        
        # Cache results for 5 minutes
        cache.set(cache_key, results_data, timeout=300)
        
        return Response(results_data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def mine(self, request):
        """
        Return all polls created by the current authenticated user.
        """
        queryset = Poll.objects.filter(created_by=request.user).select_related('category')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PollListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = PollListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

# Manage Categories
class CategoryViewSet(viewsets.ModelViewSet):
    """Full CRUD Category ViewSet"""
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]  # Allow all users full access / Update it to admin in future
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        """Queryset with annotated polls count"""
        return Category.objects.annotate(
            polls_count=Count('polls', filter=Q(polls__is_active=True))
        ).order_by('name')
    
    def list(self, request, *args, **kwargs):
        """Cached category list"""
        cache_key = "categories_list"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        response = super().list(request, *args, **kwargs)
        if response.status_code == 200:
            cache.set(cache_key, response.data, timeout=900)  # 15 minutes
        
        return response
    
    def create(self, request, *args, **kwargs):
        """Create category and clear cache"""
        response = super().create(request, *args, **kwargs)
        if response.status_code == 201:
            # Clear cache when new category is created
            cache.delete("categories_list")
        return response
    
    def update(self, request, *args, **kwargs):
        """Update category and clear cache"""
        response = super().update(request, *args, **kwargs)
        if response.status_code == 200:
            # Clear cache when category is updated
            cache.delete("categories_list")
            # Clear specific category cache if exists
            if hasattr(self.get_object(), 'id'):
                cache.delete(f"category_{self.get_object().id}_polls_count")
        return response
    
    def partial_update(self, request, *args, **kwargs):
        """Partial update category and clear cache"""
        response = super().partial_update(request, *args, **kwargs)
        if response.status_code == 200:
            cache.delete("categories_list")
            if hasattr(self.get_object(), 'id'):
                cache.delete(f"category_{self.get_object().id}_polls_count")
        return response
    
    def destroy(self, request, *args, **kwargs):
        """Delete category and clear cache"""
        category_id = self.get_object().id
        response = super().destroy(request, *args, **kwargs)
        if response.status_code == 204:
            # Clear cache when category is deleted
            cache.delete("categories_list")
            cache.delete(f"category_{category_id}_polls_count")
        return response
