"""
URL configuration for smart_registration project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

# Import viewsets and views
from courses.views import CourseViewSet, CourseSectionViewSet
from authentication.views import home

# Create API router
router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'sections', CourseSectionViewSet, basename='section')

urlpatterns = [
    # Home page
    path('', home, name='home'),
    
    # Admin interface
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', include(router.urls)),
    path('api/auth/', include('rest_framework.urls')),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Module URLs
    path('courses/', include('courses.urls')),
    path('planning/', include('planning.urls')),
    path('registration/', include('registration.urls')),
    path('recommendations/', include('ai_recommendations.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


