# authentication/management/commands/invalidate_all_tokens.py
from django.core.management.base import BaseCommand
from django.core.cache import cache
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

class Command(BaseCommand):
    help = 'Invalidate all existing JWT tokens for testing'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm you want to invalidate ALL tokens',
        )
    
    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This will invalidate ALL user sessions. '
                    'Run with --confirm to proceed.'
                )
            )
            return
        
        # Method 1: Blacklist all outstanding tokens
        outstanding_tokens = OutstandingToken.objects.all()
        blacklisted_count = 0
        
        for token in outstanding_tokens:
            # Check if already blacklisted
            if not BlacklistedToken.objects.filter(token=token).exists():
                BlacklistedToken.objects.create(token=token)
                blacklisted_count += 1
        
        # Method 2: Clear cache (for access token blacklist)
        cache.clear()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully invalidated {blacklisted_count} tokens and cleared cache'
            )
        )
