from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from polls.models import Category, Poll, Option, Vote

User = get_user_model()

class BaseTestCase(TestCase):
    """Base test case with common setup"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        self.category = Category.objects.create(
            name='Test Category',
            description='Test category for testing'
        )
        
        self.poll = Poll.objects.create(
            title='Test Poll',
            description='A test poll',
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

class BaseAPITestCase(APITestCase):
    """Base API test case with authentication"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        # Setup authentication
        self.client = APIClient()
        self.authenticate_user(self.user)
        
        # Create test data
        self.create_test_data()
    
    def authenticate_user(self, user):
        """Authenticate user and set token"""
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def create_test_data(self):
        """Create test data"""
        self.category = Category.objects.create(
            name='Technology',
            description='Tech-related polls'
        )
        
        self.poll = Poll.objects.create(
            title='Best Framework?',
            description='Choose the best web framework',
            created_by=self.user,
            category=self.category
        )
        
        self.option1 = Option.objects.create(
            poll=self.poll,
            text='Django',
            order_index=1
        )
        
        self.option2 = Option.objects.create(
            poll=self.poll,
            text='FastAPI',
            order_index=2
        )

class PollTestMixin:
    """Mixin for poll-related test utilities"""
    
    def create_poll_with_options(self, title="Test Poll", user=None, options_count=3):
        """Create poll with specified number of options"""
        if user is None:
            user = self.user
            
        poll = Poll.objects.create(
            title=title,
            created_by=user,
            category=self.category
        )
        
        options = []
        for i in range(options_count):
            option = Option.objects.create(
                poll=poll,
                text=f'Option {i+1}',
                order_index=i+1
            )
            options.append(option)
        
        return poll, options
    
    def create_votes_for_poll(self, poll, vote_distribution=None):
        """Create votes for poll with given distribution"""
        if vote_distribution is None:
            vote_distribution = [2, 1, 1]  # votes per option
        
        users = [self.user, self.user2]
        votes = []
        
        for i, option in enumerate(poll.options.all()):
            vote_count = vote_distribution[i] if i < len(vote_distribution) else 0
            
            for j in range(vote_count):
                user = users[j % len(users)]
                # Create unique user for additional votes
                if j >= len(users):
                    user = User.objects.create_user(
                        username=f'user_{poll.id}_{i}_{j}',
                        email=f'user{poll.id}{i}{j}@test.com'
                    )
                
                vote = Vote.objects.create(
                    poll=poll,
                    option=option,
                    user=user,
                    ip_address=f'192.168.1.{j+1}'
                )
                votes.append(vote)
        
        return votes

class MockRequestMixin:
    """Mixin for creating mock request objects"""
    
    def create_mock_request(self, user=None, ip='127.0.0.1'):
        """Create mock request object"""
        from django.test import RequestFactory
        
        request = RequestFactory().get('/')
        request.user = user or self.user
        request.META = {
            'REMOTE_ADDR': ip,
            'HTTP_USER_AGENT': 'Test Browser'
        }
        return request
