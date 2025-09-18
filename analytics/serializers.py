from rest_framework import serializers

class PollAnalyticsSerializer(serializers.Serializer):
    """Serializer for poll analytics data"""
    poll_id = serializers.UUIDField()
    title = serializers.CharField()
    total_votes = serializers.IntegerField()
    unique_voters = serializers.IntegerField()
    votes_per_day = serializers.ListField()
    demographics = serializers.DictField()
    engagement_rate = serializers.FloatField()
    completion_rate = serializers.FloatField()

class UserAnalyticsSerializer(serializers.Serializer):
    """Serializer for user analytics data"""
    user_id = serializers.UUIDField()
    username = serializers.CharField()
    polls_created = serializers.IntegerField()
    votes_cast = serializers.IntegerField()
    engagement_score = serializers.FloatField()
    favorite_categories = serializers.ListField()
    activity_timeline = serializers.ListField()
    