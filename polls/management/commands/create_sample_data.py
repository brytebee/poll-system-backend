from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from polls.models import Category, Poll, Option
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample data for testing'
    
    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create test user if not exists
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(f'Created user: {user.username}')
        
        # Create categories
        categories_data = [
            {'name': 'Technology', 'description': 'Tech-related polls'},
            {'name': 'Sports', 'description': 'Sports and fitness polls'},
            {'name': 'Entertainment', 'description': 'Movies, music, and fun'},
            {'name': 'Food & Drink', 'description': 'Culinary preferences'},
            {'name': 'Travel', 'description': 'Travel and destinations'},
        ]
        
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        # Create sample polls
        tech_category = Category.objects.get(name='Technology')
        sports_category = Category.objects.get(name='Sports')
        
        polls_data = [
            {
                'title': 'Which programming language is best for beginners?',
                'description': 'Help us determine the most beginner-friendly programming language',
                'category': tech_category,
                'options': ['Python', 'JavaScript', 'Java', 'C++'],
                'expires_at': timezone.now() + timedelta(days=7)
            },
            {
                'title': 'Favorite web framework?',
                'description': 'What\'s your go-to web framework for development?',
                'category': tech_category,
                'options': ['Django', 'React', 'Vue.js', 'Angular', 'Express.js'],
                'is_anonymous': True
            },
            {
                'title': 'Best sport to watch?',
                'description': 'Which sport do you enjoy watching the most?',
                'category': sports_category,
                'options': ['Football', 'Basketball', 'Soccer', 'Tennis', 'Baseball'],
                'multiple_choice': True
            }
        ]
        
        for poll_data in polls_data:
            options_data = poll_data.pop('options')
            poll, created = Poll.objects.get_or_create(
                title=poll_data['title'],
                defaults={
                    'created_by': user,
                    **poll_data
                }
            )
            
            if created:
                self.stdout.write(f'Created poll: {poll.title}')
                
                # Create options
                for index, option_text in enumerate(options_data):
                    Option.objects.create(
                        poll=poll,
                        text=option_text,
                        order_index=index + 1
                    )
                self.stdout.write(f'  Added {len(options_data)} options')
        
        self.stdout.write(
            self.style.SUCCESS('Sample data created successfully!')
        )
