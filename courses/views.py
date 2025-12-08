from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import models as django_models
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from django.views.generic import TemplateView
from .models import Course, CourseSection
from .serializers import CourseSerializer, CourseSectionSerializer


class CourseListView(TemplateView):
    """Course Catalog page view."""
    template_name = 'courses/catalog.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all available course sections
        sections = CourseSection.objects.filter(
            is_available=True,
            course__is_active=True
        ).select_related('course', 'instructor').prefetch_related('course__prerequisites').order_by('course__course_code', 'section_number')
        
        # Get available departments for filtering
        departments = Course.objects.filter(is_active=True).values_list('department', flat=True).distinct().order_by('department')
        
        # Get available terms
        terms = CourseSection.objects.filter(is_available=True).values_list('term', flat=True).distinct().order_by('term')
        
        context['sections'] = sections
        context['departments'] = departments
        context['terms'] = terms
        context['total_sections'] = sections.count()
        
        return context


course_catalog = CourseListView.as_view()


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing and searching courses.
    Provides list, retrieve, and search functionality.
    
    Filter options:
    - department: Filter by department (e.g., ?department=Computer Science)
    - level: Filter by course level (e.g., ?level=FRESHMAN)
    - credits: Filter by credit hours (e.g., ?credits=3)
    - course_number: Filter by course number extracted from code (e.g., ?course_number=101)
    - search: Search across course code, title, description, department
    """
    queryset = Course.objects.filter(is_active=True).prefetch_related('prerequisites')
    serializer_class = CourseSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'level', 'credits']
    search_fields = ['course_code', 'title', 'description', 'department']
    ordering_fields = ['course_code', 'title', 'department', 'credits']
    ordering = ['course_code']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by course number (numeric part of course code)
        course_number = self.request.query_params.get('course_number', None)
        if course_number:
            queryset = queryset.filter(course_code__icontains=course_number)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def search_catalog(self, request):
        """
        Advanced search endpoint for course catalog.
        
        Query parameters:
        - q: General search term (searches title, description, code, department)
        - department: Filter by department (also accepts 'subject' parameter)
        - course_number: Filter by course number
        - level: Filter by course level
        - credits: Filter by credit hours
        """
        queryset = self.get_queryset()
        
        # General search
        search_query = request.query_params.get('q', '')
        if search_query:
            queryset = queryset.filter(
                Q(course_code__icontains=search_query) |
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(department__icontains=search_query)
            )
        
        # Filter by department (support both 'department' and 'subject' params)
        department = request.query_params.get('department') or request.query_params.get('subject')
        if department:
            queryset = queryset.filter(department__icontains=department)
        
        # Filter by course number
        course_number = request.query_params.get('course_number')
        if course_number:
            queryset = queryset.filter(course_code__icontains=course_number)
        
        # Apply other filters
        level = request.query_params.get('level')
        if level:
            queryset = queryset.filter(level=level.upper())
        
        credits = request.query_params.get('credits')
        if credits:
            try:
                queryset = queryset.filter(credits=int(credits))
            except ValueError:
                pass
        
        # Paginate and return
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_department(self, request):
        """Get all courses grouped by department."""
        departments = Course.objects.filter(is_active=True).values_list('department', flat=True).distinct().order_by('department')
        
        result = {}
        for dept in departments:
            courses = Course.objects.filter(department=dept, is_active=True)
            result[dept] = CourseSerializer(courses, many=True).data
        
        return Response(result)


class CourseSectionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing course sections.
    Provides list, retrieve, and filtering by term/year.
    
    Filter options:
    - term: Filter by semester (e.g., ?term=Fall)
    - year: Filter by year (e.g., ?year=2024)
    - course__department: Filter by department (e.g., ?course__department=Computer Science)
    - meeting_days: Filter by meeting days (e.g., ?meeting_days=MWF)
    - course_code: Filter by course code (e.g., ?course_code=CS101)
    """
    queryset = CourseSection.objects.filter(is_available=True).select_related('course', 'instructor')
    serializer_class = CourseSectionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['term', 'year', 'course__department', 'meeting_days']
    search_fields = ['course__course_code', 'course__title', 'section_number', 'instructor__username']
    ordering_fields = ['course__course_code', 'section_number', 'start_time']
    ordering = ['course__course_code', 'section_number']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by specific course code
        course_code = self.request.query_params.get('course_code')
        if course_code:
            queryset = queryset.filter(course__course_code=course_code)
        
        # Filter by course number
        course_number = self.request.query_params.get('course_number')
        if course_number:
            queryset = queryset.filter(course__course_code__icontains=course_number)
        
        # Support 'subject' as alias for 'course__department'
        subject = self.request.query_params.get('subject')
        if subject:
            queryset = queryset.filter(course__department__icontains=subject)
        
        # Support 'semester' as alias for 'term'
        semester = self.request.query_params.get('semester')
        if semester:
            queryset = queryset.filter(term__iexact=semester)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get only sections with available seats."""
        queryset = self.get_queryset().filter(
            current_enrollment__lt=django_models.F('max_enrollment')
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search_sections(self, request):
        """
        Advanced search for course sections.
        
        Query parameters:
        - term/semester: Filter by term (e.g., Fall, Spring, Summer)
        - year: Filter by year
        - subject/department: Filter by department
        - course_code: Filter by specific course code
        - course_number: Filter by course number
        - available_only: Show only sections with available seats (true/false)
        """
        queryset = self.get_queryset()
        
        # Filter by term/semester
        term = request.query_params.get('term') or request.query_params.get('semester')
        if term:
            queryset = queryset.filter(term__iexact=term)
        
        # Filter by year
        year = request.query_params.get('year')
        if year:
            try:
                queryset = queryset.filter(year=int(year))
            except ValueError:
                pass
        
        # Filter by subject/department
        subject = request.query_params.get('subject') or request.query_params.get('department')
        if subject:
            queryset = queryset.filter(course__department__icontains=subject)
        
        # Filter by course code
        course_code = request.query_params.get('course_code')
        if course_code:
            queryset = queryset.filter(course__course_code=course_code)
        
        # Filter by course number
        course_number = request.query_params.get('course_number')
        if course_number:
            queryset = queryset.filter(course__course_code__icontains=course_number)
        
        # Filter by availability
        available_only = request.query_params.get('available_only', '').lower()
        if available_only == 'true':
            queryset = queryset.filter(
                current_enrollment__lt=django_models.F('max_enrollment')
            )
        
        # Paginate and return
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

