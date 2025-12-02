from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import models
from django_filters.rest_framework import DjangoFilterBackend
from .models import Course, CourseSection
from .serializers import CourseSerializer, CourseSectionSerializer


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing and searching courses.
    Provides list, retrieve, and search functionality.
    """
    queryset = Course.objects.filter(is_active=True).prefetch_related('prerequisites')
    serializer_class = CourseSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'level', 'credits']
    search_fields = ['course_code', 'title', 'description', 'department']
    ordering_fields = ['course_code', 'title', 'department', 'credits']
    ordering = ['course_code']


class CourseSectionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing course sections.
    Provides list, retrieve, and filtering by term/year.
    """
    queryset = CourseSection.objects.filter(is_available=True).select_related('course', 'instructor')
    serializer_class = CourseSectionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['term', 'year', 'course__department', 'meeting_days']
    search_fields = ['course__course_code', 'course__title', 'section_number', 'instructor__username']
    ordering_fields = ['course__course_code', 'section_number', 'start_time']
    ordering = ['course__course_code', 'section_number']
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get only sections with available seats."""
        queryset = self.get_queryset().filter(
            current_enrollment__lt=models.F('max_enrollment')
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

