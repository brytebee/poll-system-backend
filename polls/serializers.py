from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Category, Poll, Option, Vote

User = get_user_model()

class CategorySerializer(serializers.ModelSerializer):
    """Category serializer"""
    polls_count = serializers.ReadOnlyField(source='get_polls_count')
    
    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'slug', 'polls_count', 'created_at')
        read_only_fields = ('id', 'slug', 'created_at')

class OptionSerializer(serializers.ModelSerializer):
    """Option serializer"""
    vote_count = serializers.ReadOnlyField(source='get_vote_count')
    
    class Meta:
        model = Option
        fields = ('id', 'text', 'order_index', 'vote_count', 'created_at')
        read_only_fields = ('id', 'vote_count', 'created_at')

class OptionCreateSerializer(serializers.ModelSerializer):
    """Option creation serializer"""
    
    class Meta:
        model = Option
        fields = ('text', 'order_index')

class UserSummarySerializer(serializers.ModelSerializer):
    """Minimal user serializer for poll data"""
    
    class Meta:
        model = User
        fields = ('id', 'username', 'display_name', 'avatar')

class PollListSerializer(serializers.ModelSerializer):
    """Poll list serializer (lightweight)"""
    created_by = UserSummarySerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    total_votes = serializers.ReadOnlyField(source='get_total_votes')
    options_count = serializers.SerializerMethodField()
    is_expired = serializers.ReadOnlyField()
    can_vote = serializers.ReadOnlyField()
    
    class Meta:
        model = Poll
        fields = (
            'id', 'title', 'description', 'created_by', 'category',
            'is_active', 'is_anonymous', 'multiple_choice', 'expires_at',
            'total_votes', 'options_count', 'is_expired', 'can_vote',
            'created_at', 'updated_at'
        )
    
    def get_options_count(self, obj):
        """Get options count"""
        return obj.options.count()

class PollDetailSerializer(serializers.ModelSerializer):
    """Poll detail serializer (complete data)"""
    created_by = UserSummarySerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    options = OptionSerializer(many=True, read_only=True)
    total_votes = serializers.ReadOnlyField(source='get_total_votes')
    unique_voters = serializers.ReadOnlyField(source='get_unique_voters')
    is_expired = serializers.ReadOnlyField()
    can_vote = serializers.ReadOnlyField()
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
    
    def get_user_has_voted(self, obj):
        """Check if current user has voted"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return Vote.objects.filter(poll=obj, user=request.user).exists()

class PollCreateSerializer(serializers.ModelSerializer):
    """Poll creation serializer"""
    options = OptionCreateSerializer(many=True, write_only=True)
    category_id = serializers.UUIDField(write_only=True, required=False)
    
    class Meta:
        model = Poll
        fields = (
            'title', 'description', 'category_id', 'options',
            'is_anonymous', 'multiple_choice', 'expires_at'
        )
        extra_kwargs = {
            'title': {'max_length': 200},
            'description': {'required': False},
        }
    
    def validate_options(self, value):
        """Validate options"""
        if len(value) < 2:
            raise serializers.ValidationError("Poll must have at least 2 options")
        if len(value) > 10:
            raise serializers.ValidationError("Poll cannot have more than 10 options")
        
        # Check for duplicate option texts
        option_texts = [option['text'].strip().lower() for option in value]
        if len(option_texts) != len(set(option_texts)):
            raise serializers.ValidationError("Option texts must be unique")
        
        return value
    
    def validate_expires_at(self, value):
        """Validate expiry date"""
        if value and value <= timezone.now():
            raise serializers.ValidationError("Expiry date must be in the future")
        return value
    
    def validate_category_id(self, value):
        """Validate category exists"""
        if value:
            try:
                Category.objects.get(id=value)
            except Category.DoesNotExist:
                raise serializers.ValidationError("Invalid category ID")
        return value
    
    def create(self, validated_data):
        """Create poll with options"""
        options_data = validated_data.pop('options')
        category_id = validated_data.pop('category_id', None)
        
        # Set category if provided
        if category_id:
            validated_data['category_id'] = category_id
        
        # Set creator
        validated_data['created_by'] = self.context['request'].user
        
        # Create poll
        poll = Poll.objects.create(**validated_data)
        
        # Create options
        for index, option_data in enumerate(options_data):
            Option.objects.create(
                poll=poll,
                text=option_data['text'].strip(),
                order_index=option_data.get('order_index', index + 1)
            )
        
        return poll

class PollUpdateSerializer(serializers.ModelSerializer):
    """Poll update serializer"""
    
    class Meta:
        model = Poll
        fields = (
            'title', 'description', 'is_active', 'expires_at'
        )
    
    def validate_expires_at(self, value):
        """Validate expiry date"""
        if value and value <= timezone.now():
            raise serializers.ValidationError("Expiry date must be in the future")
        return value
    
    def update(self, instance, validated_data):
        """Update poll with validation"""
        # Don't allow changes if poll has votes and is finalized
        if instance.results_finalized and instance.get_total_votes() > 0:
            # Only allow title and description changes
            allowed_fields = ['title', 'description']
            validated_data = {
                k: v for k, v in validated_data.items() 
                if k in allowed_fields
            }
        
        return super().update(instance, validated_data)

class VoteSerializer(serializers.ModelSerializer):
    """Vote serializer"""
    poll_title = serializers.ReadOnlyField(source='poll.title')
    option_text = serializers.ReadOnlyField(source='option.text')
    voter_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Vote
        fields = (
            'id', 'poll', 'option', 'poll_title', 'option_text',
            'voter_name', 'created_at'
        )
        read_only_fields = ('id', 'created_at')
    
    def get_voter_name(self, obj):
        """Get voter name (username or Anonymous)"""
        if obj.user:
            return obj.user.display_name
        return "Anonymous"

class VoteCastSerializer(serializers.Serializer):
    """Serializer for casting votes"""
    option_id = serializers.UUIDField()
    options = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        help_text="For multiple choice polls"
    )
    
    def validate_option_id(self, value):
        """Validate option exists"""
        try:
            option = Option.objects.get(id=value)
            self.option = option
            return value
        except Option.DoesNotExist:
            raise serializers.ValidationError("Invalid option ID")
    
    def validate_options(self, value):
        """Validate multiple options for multiple choice polls"""
        if not value:
            return value
        
        # Check all options exist
        options = Option.objects.filter(id__in=value)
        if len(options) != len(value):
            raise serializers.ValidationError("One or more invalid option IDs")
        
        self.options = options
        return value
    
    def validate(self, attrs):
        """Cross-field validation"""
        poll_id = self.context.get('poll_id')
        request = self.context.get('request')
        
        try:
            poll = Poll.objects.get(id=poll_id)
        except Poll.DoesNotExist:
            raise serializers.ValidationError("Invalid poll ID")
        
        # Check if poll accepts votes
        if not poll.can_vote:
            raise serializers.ValidationError("This poll is not accepting votes")
        
        # Validate options belong to poll
        if 'option_id' in attrs:
            option = Option.objects.get(id=attrs['option_id'])
            if option.poll != poll:
                raise serializers.ValidationError("Option does not belong to this poll")
        
        if 'options' in attrs and attrs['options']:
            options = Option.objects.filter(id__in=attrs['options'])
            if not all(option.poll == poll for option in options):
                raise serializers.ValidationError("All options must belong to this poll")
            
            # Check if poll allows multiple choice
            if not poll.multiple_choice:
                raise serializers.ValidationError("This poll does not allow multiple choices")
        
        # Check for existing vote
        user = request.user if request.user.is_authenticated else None
        ip_address = self.get_client_ip(request)
        
        if user:
            # Check user hasn't voted
            if Vote.objects.filter(poll=poll, user=user).exists():
                raise serializers.ValidationError("You have already voted on this poll")
        else:
            # Check IP hasn't voted (for anonymous polls)
            if Vote.objects.filter(poll=poll, ip_address=ip_address, user__isnull=True).exists():
                raise serializers.ValidationError("This IP address has already voted on this poll")
        
        attrs['poll'] = poll
        attrs['user'] = user
        attrs['ip_address'] = ip_address
        return attrs
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def create_votes(self):
        """Create vote records"""
        validated_data = self.validated_data
        poll = validated_data['poll']
        user = validated_data['user']
        ip_address = validated_data['ip_address']
        user_agent = self.context['request'].META.get('HTTP_USER_AGENT', '')
        
        votes = []
        
        if poll.multiple_choice and 'options' in validated_data and validated_data['options']:
            # Create multiple votes
            options = Option.objects.filter(id__in=validated_data['options'])
            for option in options:
                vote = Vote.objects.create(
                    poll=poll,
                    option=option,
                    user=user,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                votes.append(vote)
        else:
            # Create single vote
            option = Option.objects.get(id=validated_data['option_id'])
            vote = Vote.objects.create(
                poll=poll,
                option=option,
                user=user,
                ip_address=ip_address,
                user_agent=user_agent
            )
            votes.append(vote)
        
        return votes
