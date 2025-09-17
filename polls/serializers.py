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
