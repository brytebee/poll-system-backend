# polls/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from django.core.cache import cache
from .models import Category, Poll, Option, Vote

User = get_user_model()

class CategorySerializer(serializers.ModelSerializer):
    """Category serializer with optimized poll count"""
    polls_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'slug', 'polls_count', 'created_at')
        read_only_fields = ('id', 'slug', 'created_at')
    
    def get_polls_count(self, obj):
        """Get cached polls count to avoid N+1 queries"""
        # Check if we have annotated count from queryset
        if hasattr(obj, 'polls_count'):
            return obj.polls_count
        
        # Fallback to cached count
        cache_key = f"category_{obj.id}_polls_count"
        count = cache.get(cache_key)
        if count is None:
            count = obj.polls.filter(is_active=True).count()
            cache.set(cache_key, count, timeout=300)  # 5 minutes
        return count

class OptionSerializer(serializers.ModelSerializer):
    """Option serializer with optimized vote count"""
    vote_count = serializers.SerializerMethodField()
    percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Option
        fields = ('id', 'text', 'order_index', 'vote_count', 'percentage', 'created_at')
        read_only_fields = ('id', 'created_at')
    
    def get_vote_count(self, obj):
        """Get vote count - use annotated value if available"""
        return getattr(obj, 'vote_count', obj.votes.count())
    
    def get_percentage(self, obj):
        """Calculate percentage of votes"""
        vote_count = self.get_vote_count(obj)
        
        # Try to get total votes from poll context
        poll = obj.poll
        if hasattr(poll, 'total_votes_count'):
            total_votes = poll.total_votes_count
        elif hasattr(poll, 'total_votes'):
            total_votes = poll.total_votes
        else:
            total_votes = poll.get_total_votes()
        
        if total_votes == 0:
            return 0
        return round((vote_count / total_votes) * 100, 2)

class PollListSerializer(serializers.ModelSerializer):
    """Optimized poll list serializer"""
    created_by = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    total_votes = serializers.SerializerMethodField()
    options_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Poll
        fields = (
            'id', 'title', 'description', 'created_by', 'category_name',
            'is_active', 'is_anonymous', 'multiple_choice', 'expires_at',
            'total_votes', 'options_count', 'is_expired', 'can_vote',
            'created_at', 'updated_at'
        )
    
    def get_created_by(self, obj):
        """Return user info without additional query"""
        return {
            'id': str(obj.created_by.id),
            'username': obj.created_by.username,
        }
    
    def get_total_votes(self, obj):
        """Get total votes using annotated value or method"""
        if hasattr(obj, 'total_votes'):
            return obj.total_votes
        return obj.get_total_votes()
    
    def get_options_count(self, obj):
        """Get options count using annotated value or method"""
        if hasattr(obj, 'options_count'):
            return obj.options_count
        return obj.options.count()

class PollDetailSerializer(serializers.ModelSerializer):
    """Optimized poll detail serializer"""
    created_by = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    options = serializers.SerializerMethodField()
    total_votes = serializers.SerializerMethodField()
    unique_voters = serializers.SerializerMethodField()
    user_has_voted = serializers.SerializerMethodField()
    
    class Meta:
        model = Poll
        fields = (
            'id', 'title', 'description', 'created_by', 'category',
            'options', 'is_active', 'is_anonymous', 'multiple_choice',
            'expires_at', 'results_finalized', 'total_votes',
            'unique_voters', 'is_expired', 'can_vote', 'user_has_voted',
            'created_at', 'updated_at'
        )
    
    def get_created_by(self, obj):
        """Return user info without additional query"""
        return {
            'id': str(obj.created_by.id),
            'username': obj.created_by.username,
            'display_name': getattr(obj.created_by, 'display_name', obj.created_by.username)
        }
    
    def get_options(self, obj):
        """Return prefetched options with vote counts"""
        options_data = []
        total_votes = self.get_total_votes(obj)
        
        for option in obj.options.all():
            vote_count = getattr(option, 'vote_count', 0)
            options_data.append({
                'id': str(option.id),
                'text': option.text,
                'order_index': option.order_index,
                'vote_count': vote_count,
                'percentage': self._calculate_percentage(vote_count, total_votes),
                'created_at': option.created_at
            })
        return options_data
    
    def _calculate_percentage(self, vote_count, total_votes):
        """Calculate vote percentage"""
        if total_votes == 0:
            return 0
        return round((vote_count / total_votes) * 100, 2)
    
    def get_total_votes(self, obj):
        """Get total votes using annotated value or method"""
        if hasattr(obj, 'total_votes_count'):
            return obj.total_votes_count
        elif hasattr(obj, 'total_votes'):
            return obj.total_votes
        return obj.get_total_votes()
    
    def get_unique_voters(self, obj):
        """Get unique voters using annotated value or method"""
        if hasattr(obj, 'unique_voters_count'):
            return obj.unique_voters_count
        elif hasattr(obj, 'unique_voters'):
            return obj.unique_voters
        return obj.get_unique_voters()
    
    def get_user_has_voted(self, obj):
        """Check if current user has voted using prefetched data"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        
        # Check if we have user_votes prefetched
        if hasattr(obj, 'user_votes'):
            return len(obj.user_votes) > 0
        
        # Fallback to database query
        return Vote.objects.filter(poll=obj, user=request.user).exists()

class PollCreateSerializer(serializers.ModelSerializer):
    """Optimized poll creation serializer with atomic transactions"""
    options = serializers.ListField(
        child=serializers.DictField(),
        min_length=2,
        max_length=10,
        write_only=True
    )
    category = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = Poll
        fields = (
            'title', 'description', 'category', 'options',
            'is_anonymous', 'multiple_choice', 'expires_at'
        )
    
    def validate_options(self, value):
        """Validate options - handle both dict and string formats"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Options must be a list")
        
        option_texts = []
        for i, option in enumerate(value):
            # Handle different option formats
            if isinstance(option, dict):
                if 'text' in option:
                    text = option['text']
                else:
                    raise serializers.ValidationError(f"Option {i+1}: Dict format must have 'text' field")
            elif isinstance(option, str):
                text = option
            else:
                raise serializers.ValidationError(f"Option {i+1}: Must be either string or dict with 'text' field")
            
            # Validate text content
            if not isinstance(text, str):
                raise serializers.ValidationError(f"Option {i+1}: Text must be a string")
            
            text = text.strip()
            if not text:
                raise serializers.ValidationError(f"Option {i+1}: Text cannot be empty")
            
            if len(text) > 500:
                raise serializers.ValidationError(f"Option {i+1}: Text cannot exceed 500 characters")
            
            option_texts.append(text)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_options = []
        for option in option_texts:
            option_lower = option.lower()
            if option_lower not in seen:
                seen.add(option_lower)
                unique_options.append(option)
        
        if len(unique_options) < 2:
            raise serializers.ValidationError("Poll must have at least 2 unique options")
        
        return unique_options
    
    def validate_category(self, value):
        """Validate category exists"""
        if value and not Category.objects.filter(id=value).exists():
            raise serializers.ValidationError("Invalid category ID")
        return value
    
    def validate_expires_at(self, value):
        """Validate expiry date"""
        if value and value <= timezone.now():
            raise serializers.ValidationError("Expiry date must be in the future")
        return value
    
    @transaction.atomic
    def create(self, validated_data):
        """Create poll with options in a single transaction"""
        options_data = validated_data.pop('options')
        category_id = validated_data.pop('category', None)
        
        # Set relationships
        validated_data['created_by'] = self.context['request'].user
        if category_id:
            validated_data['category_id'] = category_id
        
        # Create poll
        poll = Poll.objects.create(**validated_data)
        
        # Bulk create options for better performance
        option_objects = [
            Option(
                poll=poll,
                text=text,
                order_index=index + 1
            )
            for index, text in enumerate(options_data)
        ]
        Option.objects.bulk_create(option_objects)
        
        # Invalidate relevant caches
        if category_id:
            cache.delete(f"category_{category_id}_polls_count")
        
        return poll

class PollUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating polls"""
    category = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = Poll
        fields = (
            'title', 'description', 'category', 'is_active',
            'is_anonymous', 'multiple_choice', 'expires_at',
            'results_finalized', 'auto_finalize'
        )
    
    def validate_category(self, value):
        """Validate category exists"""
        if value and not Category.objects.filter(id=value).exists():
            raise serializers.ValidationError("Invalid category ID")
        return value
    
    def validate_expires_at(self, value):
        """Validate expiry date"""
        if value and value <= timezone.now():
            raise serializers.ValidationError("Expiry date must be in the future")
        return value
    
    def update(self, instance, validated_data):
        """Update poll instance"""
        category_id = validated_data.pop('category', None)
        
        if category_id is not None:
            if category_id:
                validated_data['category_id'] = category_id
            else:
                validated_data['category'] = None
        
        # Clear cache when updating
        cache.delete(f"poll_detail_{instance.id}")
        if instance.category_id:
            cache.delete(f"category_{instance.category_id}_polls_count")
        
        return super().update(instance, validated_data)

class VoteCastSerializer(serializers.Serializer):
    """Optimized vote casting serializer"""
    option_id = serializers.UUIDField(required=False)
    option_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        min_length=1,
        max_length=10
    )
    
    def validate(self, attrs):
        """Validate that either option_id or option_ids is provided"""
        option_id = attrs.get('option_id')
        option_ids = attrs.get('option_ids')
        
        if not option_id and not option_ids:
            raise serializers.ValidationError("Either option_id or option_ids must be provided")
        
        if option_id and option_ids:
            raise serializers.ValidationError("Provide either option_id or option_ids, not both")
        
        # Normalize to option_ids list
        if option_id:
            option_ids = [option_id]
        
        attrs['option_ids'] = option_ids
        return self.validate_options_and_poll(attrs)
    
    def validate_options_and_poll(self, attrs):
        """Validate options exist and belong to same poll"""
        option_ids = attrs['option_ids']
        poll = self.context.get('poll')
        
        # Single query to get all options with poll info
        if poll:
            options = Option.objects.filter(id__in=option_ids, poll=poll)
        else:
            options = Option.objects.select_related('poll').filter(id__in=option_ids)
            if options:
                poll = options[0].poll
                # Check all options belong to same poll
                if not all(option.poll.id == poll.id for option in options):
                    raise serializers.ValidationError("All options must belong to the same poll")
        
        if len(options) != len(option_ids):
            raise serializers.ValidationError("One or more invalid option IDs")
        
        self.poll = poll
        self.options = list(options)
        
        return self.cross_validate(attrs)
    
    def cross_validate(self, attrs):
        """Cross-field validation with optimized queries"""
        poll = self.poll
        options = self.options
        request = self.context.get('request')
        
        # Validate poll state
        if not poll.is_active:
            raise serializers.ValidationError("Poll is not active")
        
        if poll.expires_at and poll.expires_at <= timezone.now():
            raise serializers.ValidationError("Poll has expired")
        
        # Validate multiple choice
        if len(options) > 1 and not poll.multiple_choice:
            raise serializers.ValidationError("This poll does not allow multiple choices")
        
        # Check for existing votes
        user = request.user if request.user.is_authenticated else None
        ip_address = self._get_client_ip(request)
        
        existing_votes_query = Vote.objects.filter(poll=poll)
        if user:
            existing_votes_query = existing_votes_query.filter(user=user)
        else:
            existing_votes_query = existing_votes_query.filter(
                ip_address=ip_address, 
                user__isnull=True
            )
        
        if existing_votes_query.exists():
            voter_type = "user" if user else "IP address"
            raise serializers.ValidationError(f"This {voter_type} has already voted on this poll")
        
        attrs.update({
            'poll': poll,
            'options': options,
            'user': user,
            'ip_address': ip_address
        })
        return attrs
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
    
    @transaction.atomic
    def create_votes(self):
        """Create votes with optimized bulk operations"""
        validated_data = self.validated_data
        poll = validated_data['poll']
        options = validated_data['options']
        user = validated_data['user']
        ip_address = validated_data['ip_address']
        user_agent = self.context['request'].META.get('HTTP_USER_AGENT', '')[:500]
        
        # Bulk create votes
        vote_objects = [
            Vote(
                poll=poll,
                option=option,
                user=user,
                ip_address=ip_address,
                user_agent=user_agent
            )
            for option in options
        ]
        
        created_votes = Vote.objects.bulk_create(vote_objects)
        
        # Update poll cache
        cache_key = f"poll_{poll.id}_total_votes"
        cache.delete(cache_key)
        
        # Update category cache if exists
        if poll.category_id:
            cache.delete(f"category_{poll.category_id}_polls_count")
        
        return created_votes