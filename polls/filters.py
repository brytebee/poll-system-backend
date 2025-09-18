import django_filters
from django.db.models import Q
from .models import Poll, Category

class PollFilter(django_filters.FilterSet):
    """Advanced filtering for polls"""
    
    title = django_filters.CharFilter(
        field_name='title',
        lookup_expr='icontains',
        label='Title contains'
    )
    
    description = django_filters.CharFilter(
        field_name='description',
        lookup_expr='icontains',
        label='Description contains'
    )
    
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        field_name='category',
        label='Category'
    )
    
    created_by__username = django_filters.CharFilter(
        field_name='created_by__username',
        lookup_expr='icontains',
        label='Creator username'
    )
    
    is_active = django_filters.BooleanFilter(
        field_name='is_active',
        label='Active polls only'
    )
    
    is_anonymous = django_filters.BooleanFilter(
        field_name='is_anonymous',
        label='Anonymous polls only'
    )
    
    multiple_choice = django_filters.BooleanFilter(
        field_name='multiple_choice',
        label='Multiple choice polls only'
    )
    
    has_expiry = django_filters.BooleanFilter(
        method='filter_has_expiry',
        label='Has expiry date'
    )
    
    min_votes = django_filters.NumberFilter(
        method='filter_min_votes',
        label='Minimum vote count'
    )
    
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        label='Created after'
    )
    
    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        label='Created before'
    )
    
    search = django_filters.CharFilter(
        method='search_polls',
        label='Search polls'
    )
    
    class Meta:
        model = Poll
        fields = []
    
    def filter_has_expiry(self, queryset, name, value):
        """Filter polls with/without expiry"""
        if value is True:
            return queryset.filter(expires_at__isnull=False)
        elif value is False:
            return queryset.filter(expires_at__isnull=True)
        return queryset
    
    def filter_min_votes(self, queryset, name, value):
        """Filter polls with minimum vote count"""
        from django.db.models import Count
        return queryset.annotate(
            vote_count=Count('votes')
        ).filter(vote_count__gte=value)
    
    def search_polls(self, queryset, name, value):
        """Advanced search across multiple fields"""
        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value) |
            Q(options__text__icontains=value) |
            Q(created_by__username__icontains=value) |
            Q(created_by__first_name__icontains=value) |
            Q(created_by__last_name__icontains=value)
        ).distinct()
    