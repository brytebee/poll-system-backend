# admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Poll, Option, Vote, PollResult, VoteSession

class IsAnonymousFilter(admin.SimpleListFilter):
    """Custom filter for anonymous votes"""
    title = 'Vote Type'
    parameter_name = 'is_anonymous'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Anonymous'),
            ('no', 'Registered User'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(user__isnull=True)
        if self.value() == 'no':
            return queryset.filter(user__isnull=False)
        return queryset

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for Category"""
    list_display = ('name', 'slug', 'get_polls_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('id', 'created_at', 'updated_at')

@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    """Admin configuration for Poll"""
    list_display = (
        'title', 'created_by', 'category', 'is_active',
        'is_anonymous', 'expires_at', 'get_total_votes'
    )
    list_filter = (
        'is_active', 'is_anonymous', 'multiple_choice',
        'category', 'created_at', 'expires_at'
    )
    search_fields = ('title', 'description', 'created_by__username')
    readonly_fields = (
        'id', 'created_at', 'updated_at', 'get_total_votes',
        'get_unique_voters'
    )
    autocomplete_fields = ['created_by', 'category']
    date_hierarchy = 'created_at'

class OptionInline(admin.TabularInline):
    """Inline admin for poll options"""
    model = Option
    extra = 3
    fields = ('text', 'order_index')
    ordering = ('order_index',)

@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    """Admin configuration for Option"""
    list_display = ('text', 'poll', 'order_index', 'get_vote_count')
    list_filter = ('poll__category', 'created_at')
    search_fields = ('text', 'poll__title')
    readonly_fields = ('id', 'created_at', 'get_vote_count')
    autocomplete_fields = ['poll']

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    """Admin configuration for Vote"""
    list_display = (
        'poll', 'option', 'user', 'ip_address', 'created_at'
    )
    list_filter = (
        'poll__category', 'created_at', IsAnonymousFilter
    )
    search_fields = (
        'poll__title', 'option__text', 'user__username', 'ip_address'
    )
    readonly_fields = ('id', 'created_at')
    autocomplete_fields = ['poll', 'option', 'user']
    date_hierarchy = 'created_at'

@admin.register(PollResult)
class PollResultAdmin(admin.ModelAdmin):
    """Admin configuration for PollResult"""
    list_display = (
        'poll', 'option', 'vote_count', 'percentage', 'rank'
    )
    list_filter = ('poll__category', 'created_at')
    search_fields = ('poll__title', 'option__text')
    readonly_fields = ('id', 'created_at', 'updated_at')
    autocomplete_fields = ['poll', 'option']

@admin.register(VoteSession)
class VoteSessionAdmin(admin.ModelAdmin):
    """Admin configuration for VoteSession"""
    list_display = (
        'session_key', 'ip_address', 'created_at', 
        'expires_at', 'is_expired'
    )
    list_filter = ('created_at', 'expires_at')
    search_fields = ('session_key', 'ip_address')
    readonly_fields = ('id', 'created_at', 'is_expired')
    
    actions = ['cleanup_expired_sessions']
    
    def cleanup_expired_sessions(self, request, queryset):
        """Admin action to cleanup expired sessions"""
        count = VoteSession.cleanup_expired()[0]
        self.message_user(
            request,
            f"Cleaned up {count} expired sessions"
        )
    cleanup_expired_sessions.short_description = "Clean up expired sessions"
