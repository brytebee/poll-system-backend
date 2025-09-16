from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import Category, Poll, Option, Vote

User = get_user_model()

class CategoryModelTests(TestCase):
    """Test cases for Category model"""
    
    def test_category_creation(self):
        """Test category creation"""
        category = Category.objects.create(
            name='Technology',
            description='Tech related polls'
        )
        self.assertEqual(category.name, 'Technology')
        self.assertEqual(category.slug, 'technology')
    
    def test_category_str_representation(self):
        """Test category string representation"""
        category = Category.objects.create(name='Sports')
        self.assertEqual(str(category), 'Sports')

class PollModelTests(TestCase):
    """Test cases for Poll model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='General')
    
    def test_poll_creation(self):
        """Test poll creation"""
        poll = Poll.objects.create(
            title='Test Poll',
            description='A test poll',
            created_by=self.user,
            category=self.category
        )
        self.assertEqual(poll.title, 'Test Poll')
        self.assertEqual(poll.created_by, self.user)
        self.assertTrue(poll.is_active)
        self.assertTrue(poll.can_vote)
    
    def test_poll_expiry(self):
        """Test poll expiry functionality"""
        # Create expired poll
        expired_poll = Poll.objects.create(
            title='Expired Poll',
            created_by=self.user,
            category=self.category,
            expires_at=timezone.now() - timedelta(hours=1)
        )
        self.assertTrue(expired_poll.is_expired)
        self.assertFalse(expired_poll.can_vote)
        
        # Create future poll
        future_poll = Poll.objects.create(
            title='Future Poll',
            created_by=self.user,
            category=self.category,
            expires_at=timezone.now() + timedelta(hours=1)
        )
        self.assertFalse(future_poll.is_expired)
        self.assertTrue(future_poll.can_vote)

class VoteModelTests(TestCase):
    """Test cases for Vote model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='General')
        self.poll = Poll.objects.create(
            title='Test Poll',
            created_by=self.user,
            category=self.category
        )
        self.option1 = Option.objects.create(
            poll=self.poll,
            text='Option 1',
            order_index=1
        )
        self.option2 = Option.objects.create(
            poll=self.poll,
            text='Option 2',
            order_index=2
        )
    
    def test_vote_creation(self):
        """Test vote creation"""
        vote = Vote.objects.create(
            poll=self.poll,
            option=self.option1,
            user=self.user,
            ip_address='192.168.1.1'
        )
        self.assertEqual(vote.poll, self.poll)
        self.assertEqual(vote.option, self.option1)
        self.assertEqual(vote.user, self.user)
    
    def test_vote_counting(self):
        """Test vote counting functionality"""
        # Create votes
        Vote.objects.create(
            poll=self.poll,
            option=self.option1,
            user=self.user,
            ip_address='192.168.1.1'
        )
        
        user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123'
        )
        Vote.objects.create(
            poll=self.poll,
            option=self.option2,
            user=user2,
            ip_address='192.168.1.2'
        )
        
        # Test counts
        self.assertEqual(self.poll.get_total_votes(), 2)
        self.assertEqual(self.option1.get_vote_count(), 1)
        self.assertEqual(self.option2.get_vote_count(), 1)
        
        # Test percentages
        self.assertEqual(self.option1.get_vote_percentage(), 50.0)
        self.assertEqual(self.option2.get_vote_percentage(), 50.0)
