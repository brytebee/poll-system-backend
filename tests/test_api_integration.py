from django.urls import reverse
from rest_framework import status
from polls.models import Poll, Vote, Category, Option
from .test_utils import BaseAPITestCase, PollTestMixin

class PollAPIIntegrationTest(BaseAPITestCase, PollTestMixin):
    """Integration tests for Poll API"""
    
    def test_poll_creation_workflow(self):
        """Test complete poll creation workflow"""
        url = reverse('polls:poll-list')
        data = {
            'title': 'Integration Test Poll',
            'description': 'Testing the complete workflow',
            'category_id': str(self.category.id),
            'options': [
                {'text': 'Option A', 'order_index': 1},
                {'text': 'Option B', 'order_index': 2},
                {'text': 'Option C', 'order_index': 3}
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Integration Test Poll')
        self.assertEqual(len(response.data['options']), 3)
        
        # Verify database
        poll = Poll.objects.get(id=response.data['id'])
        self.assertEqual(poll.options.count(), 3)
        self.assertEqual(poll.created_by, self.user)
    
    def test_voting_workflow(self):
        """Test complete voting workflow"""
        # Step 1: Create poll
        poll, options = self.create_poll_with_options(
            title='Voting Test Poll',
            options_count=3
        )
        
        # Step 2: Vote on poll
        vote_url = reverse('polls:poll-vote', kwargs={'pk': poll.id})
        vote_data = {'option_id': str(options[0].id)}
        
        response = self.client.post(vote_url, vote_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Vote cast successfully')
        
        # Step 3: Verify vote was recorded
        vote = Vote.objects.get(poll=poll, user=self.user)
        self.assertEqual(vote.option, options[0])
        
        # Step 4: Check results
        results_url = reverse('polls:poll-results', kwargs={'pk': poll.id})
        response = self.client.get(results_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_votes'], 1)
        self.assertEqual(response.data['results'][0]['vote_count'], 1)
        
        # Step 5: Try to vote again (should fail)
        response = self.client.post(vote_url, vote_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_multiple_choice_voting_workflow(self):
        """Test multiple choice voting workflow"""
        # Create multiple choice poll
        poll = Poll.objects.create(
            title='Multiple Choice Poll',
            created_by=self.user,
            multiple_choice=True
        )
        
        options = []
        for i in range(4):
            option = Option.objects.create(
                poll=poll,
                text=f'MC Option {i+1}',
                order_index=i+1
            )
            options.append(option)
        
        # Vote for multiple options
        vote_url = reverse('polls:poll-vote', kwargs={'pk': poll.id})
        vote_data = {
            'options': [str(options[0].id), str(options[2].id)]
        }
        
        response = self.client.post(vote_url, vote_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['votes_count'], 2)
        
        # Verify votes were recorded
        user_votes = Vote.objects.filter(poll=poll, user=self.user)
        self.assertEqual(user_votes.count(), 2)
        
        voted_options = list(user_votes.values_list('option__id', flat=True))
        self.assertIn(options[0].id, voted_options)
        self.assertIn(options[2].id, voted_options)
    
    def test_poll_finalization_workflow(self):
        """Test poll finalization workflow"""
        poll, options = self.create_poll_with_options()
        
        # Create some votes
        self.create_votes_for_poll(poll, [5, 3, 2])
        
        # Finalize poll
        finalize_url = reverse('polls:poll-finalize', kwargs={'pk': poll.id})
        response = self.client.post(finalize_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('finalized successfully', response.data['message'])
        
        # Check poll status
        poll.refresh_from_db()
        self.assertTrue(poll.results_finalized)
        self.assertFalse(poll.is_active)
        
        # Check results were saved
        self.assertEqual(poll.results.count(), 3)
        
        # Check rankings are correct
        top_result = poll.results.filter(rank=1).first()
        self.assertEqual(top_result.vote_count, 5)
        
        # Try to vote on finalized poll (should fail)
        vote_url = reverse('polls:poll-vote', kwargs={'pk': poll.id})
        vote_data = {'option_id': str(options[0].id)}
        
        # Switch to different user
        self.authenticate_user(self.user2)
        response = self.client.post(vote_url, vote_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_anonymous_voting_workflow(self):
        """Test anonymous voting workflow"""
        # Create anonymous poll
        poll = Poll.objects.create(
            title='Anonymous Poll',
            created_by=self.user,
            is_anonymous=True
        )
        
        option = Option.objects.create(
            poll=poll,
            text='Anonymous Option',
            order_index=1
        )
        
        # Logout user
        self.client.credentials()
        
        # Vote anonymously
        vote_url = reverse('polls:poll-vote', kwargs={'pk': poll.id})
        vote_data = {'option_id': str(option.id)}
        
        response = self.client.post(vote_url, vote_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify anonymous vote was recorded
        vote = Vote.objects.get(poll=poll)
        self.assertIsNone(vote.user)
        self.assertIsNotNone(vote.ip_address)
    
    def test_poll_filtering_and_search(self):
        """Test poll filtering and search functionality"""
        # Create various polls
        tech_category = Category.objects.create(name='Technology', slug='technology')
        sports_category = Category.objects.create(name='Sports', slug='sports')
        
        polls = [
            Poll.objects.create(
                title='Python vs Java',
                description='Programming language comparison',
                created_by=self.user,
                category=tech_category
            ),
            Poll.objects.create(
                title='Football Championship',
                description='Best team prediction',
                created_by=self.user2,
                category=sports_category
            ),
            Poll.objects.create(
                title='Favorite IDE',
                description='Development environment preferences',
                created_by=self.user,
                category=tech_category,
                is_active=False
            )
        ]
        
        url = reverse('polls:poll-list')
        
        # Test category filtering
        response = self.client.get(url, {'category': tech_category.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)  # 2 tech polls + 1 from setup
        
        # Test active filtering
        response = self.client.get(url, {'is_active': True})
        active_polls = [p for p in response.data['results'] if p['is_active']]
        self.assertEqual(len(active_polls), 3)  # All active polls
        
        # Test search
        response = self.client.get(url, {'search': 'Python'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
        
        # Test ordering
        response = self.client.get(url, {'ordering': 'title'})
        titles = [p['title'] for p in response.data['results']]
        self.assertEqual(titles, sorted(titles))

class AnalyticsAPIIntegrationTest(BaseAPITestCase, PollTestMixin):
    """Integration tests for Analytics API"""
    
    def test_poll_analytics_workflow(self):
        """Test poll analytics data generation"""
        poll, options = self.create_poll_with_options(options_count=3)
        
        # Create votes over time
        self.create_votes_for_poll(poll, [10, 5, 3])
        
        # Get analytics
        from analytics.services import AnalyticsService
        analytics = AnalyticsService.get_poll_analytics(poll)
        
        self.assertEqual(analytics['total_votes'], 18)
        self.assertGreater(analytics['engagement_rate'], 0)
        self.assertEqual(len(analytics['results']), 3)
    
    def test_user_analytics_workflow(self):
        """Test user analytics data generation"""
        # Create multiple polls and votes for user
        for i in range(3):
            poll, options = self.create_poll_with_options(
                title=f'User Poll {i+1}',
                user=self.user
            )
            self.create_votes_for_poll(poll, [2, 1, 1])
        
        # Get user analytics
        from analytics.services import AnalyticsService
        analytics = AnalyticsService.get_user_analytics(self.user)
        
        self.assertEqual(analytics['polls_created'], 4)  # 3 + 1 from setup
        self.assertGreater(analytics['engagement_score'], 0)
        self.assertIsInstance(analytics['favorite_categories'], list)
    
    def test_system_health_metrics(self):
        """Test system health metrics"""
        # Create some activity
        self.create_poll_with_options()
        
        from analytics.services import AnalyticsService
        metrics = AnalyticsService.get_system_health_metrics()
        
        self.assertIn('database', metrics)
        self.assertIn('activity', metrics)
        self.assertIn('performance', metrics)
        
        self.assertGreater(metrics['database']['total_polls'], 0)
        self.assertGreaterEqual(metrics['performance']['avg_votes_per_poll'], 0)
      