from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()

class UserModelTests(TestCase):
    """Test cases for CustomUser model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_user_creation(self):
        """Test user creation"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('testpass123'))
    
    def test_user_str_representation(self):
        """Test user string representation"""
        self.assertEqual(str(self.user), 'testuser')
    
    def test_full_name_property(self):
        """Test full_name property"""
        self.assertEqual(self.user.full_name, 'Test User')
    
    def test_display_name_property(self):
        """Test display_name property"""
        self.assertEqual(self.user.display_name, 'Test User')
        
        # Test with user without first/last name
        user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123'
        )
        self.assertEqual(user2.display_name, 'user2')

class AuthenticationAPITests(APITestCase):
    """Test cases for authentication APIs"""
    
    def test_user_registration(self):
        """Test user registration"""
        url = reverse('authentication:register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertIn('tokens', response.data)
    
    def test_user_login(self):
        """Test user login"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        url = reverse('authentication:login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('user', response.data)
    
    def test_check_username_availability(self):
        """Test username availability check"""
        User.objects.create_user(
            username='taken',
            email='taken@example.com',
            password='pass123'
        )
        
        url = reverse('authentication:check_username')
        
        # Test taken username
        response = self.client.get(url, {'username': 'taken'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['available'])
        
        # Test available username
        response = self.client.get(url, {'username': 'available'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['available'])
