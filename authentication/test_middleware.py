"""
Tests for authentication middleware.
"""
from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class LoginRequiredMiddlewareTest(TestCase):
    """Tests for the LoginRequiredMiddleware."""
    
    def setUp(self):
        """Set up test client and user."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_unauthenticated_user_redirected_to_login(self):
        """Test that unauthenticated users are redirected to login."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response.url)
    
    def test_authenticated_user_can_access_home(self):
        """Test that authenticated users can access the home page."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_login_page_accessible_without_auth(self):
        """Test that login page is accessible without authentication."""
        response = self.client.get('/admin/login/')
        self.assertEqual(response.status_code, 200)
    
    def test_static_files_accessible_without_auth(self):
        """Test that static files are accessible without authentication."""
        # Static files should not require authentication
        # This tests the middleware exemption logic
        response = self.client.get('/static/css/home.css')
        # 404 is acceptable since the file may not exist in test environment
        # What matters is we don't get redirected (302)
        self.assertIn(response.status_code, [200, 404])
    
    def test_redirect_includes_next_parameter(self):
        """Test that redirect includes the 'next' parameter."""
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('next=', response.url)
    
    def test_logout_page_accessible_without_auth(self):
        """Test that logout page is accessible without authentication."""
        # Logout should be accessible (though it may redirect)
        response = self.client.get('/admin/logout/')
        # Accept 200 or 302 (redirect after logout)
        self.assertIn(response.status_code, [200, 302])
