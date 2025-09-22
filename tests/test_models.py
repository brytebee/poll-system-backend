from django.utils import timezone
from datetime import timedelta
from polls.models import Category, Poll, Vote
from .test_utils import BaseTestCase, PollTestMixin

class CategoryModelTest(BaseTestCase):
    """Test Category model"""
    
    def test_category_creation(self):
        """Test category creation with slug generation"""
        category = Category.objects.create(name='New Technology')
        self.assertEqual(category.slug, 'new-technology')
        self.assertEqual(str(category), 'New Technology')
    
    def test_category_unique_name(self):
        """Test category name uniqueness"""
        with self.assertRaises(Exception):
            Category.objects.create(name='Test Category')  # Already exists in setup
    
    def test_get_polls_count(self):
        """Test get_polls_count method"""
        self.assertEqual(self.category.get_polls_count(), 1)
        
        # Create inactive poll
        Poll.objects.create(
            title='Inactive Poll',
            created_by=self.user,
            category=self.category,
            is_active=False
        )
        
        # Should still return 1 (only active polls)
        self.assertEqual(self.category.get_polls_count(), 1)

class PollModelTest(BaseTestCase, PollTestMixin):
    """Test Poll model"""
    
    def test_poll_creation(self):
        """Test basic poll creation"""
        self.assertEqual(self.poll.title, 'Test Poll')
        self.assertEqual(self.poll.created_by, self.user)
        self.assertTrue(self.poll.is_active)
        self.assertTrue(self.poll.can_vote)
        self.assertEqual(str(self.poll), 'Test Poll')
    
    def test_poll_expiry(self):
        """Test poll expiry functionality"""
        # Create expired poll
        expired_poll = Poll.objects.create(
            title='Expired Poll',
            created_by=self.user,
            expires_at=timezone.now() - timedelta(hours=1)
        )
        
        self.assertTrue(expired_poll.is_expired)
        self.assertFalse(expired_poll.can_vote)
        self.assertEqual(expired_poll.status, 'expired')
    
    def test_poll_scheduling(self):
        """Test poll scheduling functionality"""
        # Create future poll
        future_poll = Poll.objects.create(
            title='Future Poll',
            created_by=self.user,
            starts_at=timezone.now() + timedelta(hours=1)
        )
        
        self.assertTrue(future_poll.is_scheduled)
        self.assertFalse(future_poll.can_vote)
        self.assertEqual(future_poll.status, 'scheduled')
    
    def test_poll_vote_counts(self):
        """Test vote counting methods"""
        self.assertEqual(self.poll.get_total_votes(), 0)
        self.assertEqual(self.poll.get_unique_voters(), 0)
        
        # Create some votes
        self.create_votes_for_poll(self.poll, [2, 1])
        
        self.assertEqual(self.poll.get_total_votes(), 3)
        self.assertEqual(self.poll.get_unique_voters(), 2)
    
    def test_poll_finalization(self):
        """Test poll result finalization"""
        self.assertFalse(self.poll.results_finalized)
        
        # Create votes and finalize
        self.create_votes_for_poll(self.poll, [3, 2])
        
        from polls.services.results_service import PollResultsService
        success, message = PollResultsService.finalize_poll_results(self.poll)
        
        self.assertTrue(success)
        self.poll.refresh_from_db()
        self.assertTrue(self.poll.results_finalized)
        self.assertFalse(self.poll.is_active)
        
        # Check results were created
        self.assertEqual(self.poll.results.count(), 2)
        
        # Check rankings
        top_result = self.poll.results.filter(rank=1).first()
        self.assertEqual(top_result.vote_count, 3)

class VoteModelTest(BaseTestCase):
    """Test Vote model"""
    
    def test_vote_creation(self):
        """Test basic vote creation"""
        vote = Vote.objects.create(
            poll=self.poll,
            option=self.option1,
            user=self.user,
            ip_address='192.168.1.1'
        )
        
        self.assertEqual(vote.poll, self.poll)
        self.assertEqual(vote.option, self.option1)
        self.assertEqual(vote.user, self.user)
    
    def test_vote_constraints(self):
        """Test vote uniqueness constraints"""
        # Create first vote
        Vote.objects.create(
            poll=self.poll,
            option=self.option1,
            user=self.user,
            ip_address='192.168.1.1'
        )
        
        # Try to create duplicate vote (should fail)
        with self.assertRaises(Exception):
            Vote.objects.create(
                poll=self.poll,
                option=self.option2,  # Different option, same user
                user=self.user,
                ip_address='192.168.1.1'
            )
    
    def test_anonymous_vote_constraints(self):
        """Test anonymous vote IP constraints"""
        # Create anonymous vote
        Vote.objects.create(
            poll=self.poll,
            option=self.option1,
            user=None,
            ip_address='192.168.1.1'
        )
        
        # Try to create duplicate anonymous vote from same IP
        with self.assertRaises(Exception):
            Vote.objects.create(
                poll=self.poll,
                option=self.option2,
                user=None,
                ip_address='192.168.1.1'
            )
    
    def test_vote_string_representation(self):
        """Test vote string representation"""
        vote = Vote.objects.create(
            poll=self.poll,
            option=self.option1,
            user=self.user,
            ip_address='192.168.1.1'
        )
        
        expected = f"{self.user.username} voted for Option 1 in Test Poll"
        self.assertIn("voted for", str(vote))
        self.assertIn(self.user.username, str(vote))
