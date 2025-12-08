"""
Authentication middleware to enforce login requirements across the application.
"""
from django.shortcuts import redirect
from django.conf import settings


class LoginRequiredMiddleware:
    """
    Middleware that requires authentication for all views except login/logout.
    Unauthenticated users are redirected to the login page.
    """
    
    # URLs that don't require authentication
    EXEMPT_URLS = [
        '/admin/login/',
        '/admin/logout/',
        '/admin/password_reset',
        '/accounts/login/',
        '/accounts/logout/',
        '/static/',
        '/media/',
        '/api/',  # API endpoints handle their own authentication via DRF
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            # Check if the current path is in exempt URLs
            path = request.path_info
            
            # Allow access to exempt URLs (including admin login which is handled by Django/CAS)
            if not any(path.startswith(exempt) for exempt in self.EXEMPT_URLS):
                # Redirect to admin login page (which will use CAS)
                login_url = getattr(settings, 'LOGIN_URL', '/admin/login/')
                # Include next parameter if not already in URL
                if '?' not in login_url:
                    return redirect(f'{login_url}?next={path}')
                return redirect(login_url)
        
        response = self.get_response(request)
        return response
