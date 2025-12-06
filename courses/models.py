from django.db import models
from django.utils.translation import gettext_lazy as _
from authentication.models import User


class Course(models.Model):
    """Model representing a university course."""
    
    course_code = models.CharField(
        max_length=20,
        unique=True,
        help_text=_('Unique course code (e.g., CS101)')
    )
    
    title = models.CharField(
        max_length=200,
        help_text=_('Course title')
    )
    
    description = models.TextField(
        help_text=_('Detailed course description')
    )
    
    credits = models.IntegerField(
        default=3,
        help_text=_('Number of credit hours')
    )
    
    department = models.CharField(
        max_length=100,
        help_text=_('Department offering the course'),
        db_index=True  # Added index for faster filtering
    )
    
    level = models.CharField(
        max_length=20,
        choices=[
            ('FRESHMAN', 'Freshman'),
            ('SOPHOMORE', 'Sophomore'),
            ('JUNIOR', 'Junior'),
            ('SENIOR', 'Senior'),
            ('GRADUATE', 'Graduate'),
        ],
        default='FRESHMAN'
    )
    
    prerequisites = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='prerequisite_for',
        help_text=_('Prerequisites for this course')
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text=_('Whether the course is currently active')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'courses'
        verbose_name = _('Course')
        verbose_name_plural = _('Courses')
        ordering = ['course_code']
        indexes = [
            models.Index(fields=['department', 'level']),
        ]
    
    def __str__(self):
        return f"{self.course_code} - {self.title}"
    
    def get_course_number(self):
        """Extract numeric portion from course code (e.g., '101' from 'CS101')"""
        import re
        match = re.search(r'\d+', self.course_code)
        return match.group() if match else ''


class CourseSection(models.Model):
    """Model representing a specific section of a course in a given term."""
    
    class DayOfWeek(models.TextChoices):
        MONDAY = 'MON', _('Monday')
        TUESDAY = 'TUE', _('Tuesday')
        WEDNESDAY = 'WED', _('Wednesday')
        THURSDAY = 'THU', _('Thursday')
        FRIDAY = 'FRI', _('Friday')
        SATURDAY = 'SAT', _('Saturday')
        SUNDAY = 'SUN', _('Sunday')
    
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='sections'
    )
    
    section_number = models.CharField(
        max_length=10,
        help_text=_('Section number (e.g., 001, A01)')
    )
    
    term = models.CharField(
        max_length=20,
        help_text=_('Academic term (e.g., Fall, Spring, Summer)'),
        db_index=True  # Added index for faster filtering
    )
    
    year = models.IntegerField(
        help_text=_('Academic year'),
        db_index=True  # Added index for faster filtering
    )
    
    instructor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='taught_sections'
    )
    
    max_enrollment = models.IntegerField(
        default=30,
        help_text=_('Maximum number of students allowed')
    )
    
    current_enrollment = models.IntegerField(
        default=0,
        help_text=_('Current number of enrolled students')
    )
    
    location = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('Room/building location')
    )
    
    meeting_days = models.CharField(
        max_length=50,
        help_text=_('Days the class meets (e.g., MWF, TTH)')
    )
    
    start_time = models.TimeField(
        help_text=_('Class start time')
    )
    
    end_time = models.TimeField(
        help_text=_('Class end time')
    )
    
    is_available = models.BooleanField(
        default=True,
        help_text=_('Whether section is available for registration')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'course_sections'
        verbose_name = _('Course Section')
        verbose_name_plural = _('Course Sections')
        unique_together = [['course', 'section_number', 'term', 'year']]
        ordering = ['course__course_code', 'section_number']
        indexes = [
            models.Index(fields=['term', 'year']),
            models.Index(fields=['is_available']),
        ]
    
    def __str__(self):
        return f"{self.course.course_code}-{self.section_number} ({self.term} {self.year})"
    
    def is_full(self):
        return self.current_enrollment >= self.max_enrollment
    
    def available_seats(self):
        return max(0, self.max_enrollment - self.current_enrollment)

