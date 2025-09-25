# polls/management/commands/optimize_db.py
from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.core.cache import cache

class Command(BaseCommand):
    help = 'Optimize database performance with indexes and cleanup'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-cache',
            action='store_true',
            help='Clear all caches',
        )
        parser.add_argument(
            '--analyze',
            action='store_true',
            help='Analyze database tables',
        )
    
    def handle(self, *args, **options):
        if options['clear_cache']:
            self.stdout.write('Clearing caches...')
            cache.clear()
            self.stdout.write(self.style.SUCCESS('Caches cleared'))
        
        if options['analyze']:
            self.stdout.write('Analyzing database tables...')
            with connection.cursor() as cursor:
                # PostgreSQL specific - adjust for other databases
                cursor.execute("ANALYZE;")
            self.stdout.write(self.style.SUCCESS('Database analysis complete'))
        
        self.stdout.write('Creating optimized indexes...')
        self._create_indexes()
        
        self.stdout.write(self.style.SUCCESS('Database optimization complete'))
    
    def _create_indexes(self):
        """Create performance indexes"""
        with connection.cursor() as cursor:
            # Composite indexes for common queries
            indexes = [
                'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_poll_active_created ON polls_poll(is_active, created_at DESC) WHERE is_active = true;',
                
                'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_vote_poll_user ON polls_vote(poll_id, user_id) WHERE user_id IS NOT NULL;',
                
                'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_vote_poll_ip ON polls_vote(poll_id, ip_address) WHERE user_id IS NULL;',
                
                'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_poll_category_active ON polls_poll(category_id, is_active) WHERE is_active = true;',
                
                'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_vote_created_at ON polls_vote(created_at DESC);'
            ]
            
            for index_sql in indexes:
                try:
                    cursor.execute(index_sql)
                    self.stdout.write(f'Created index: {index_sql.split("IF NOT EXISTS")[1].split("ON")[0].strip()}')
                except Exception as e:
                    self.stdout.write(f'Index creation failed: {str(e)}')
