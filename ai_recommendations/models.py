from django.db import models
from django.utils.translation import gettext_lazy as _
from authentication.models import User
from courses.models import Course


class DegreeRequirement(models.Model):
    """Model representing degree requirements for various majors."""
    
    major = models.CharField(
        max_length=100,
        help_text=_('Major/program name')
    )
    
    requirement_type = models.CharField(
        max_length=50,
        choices=[
            ('CORE', 'Core Requirement'),
            ('ELECTIVE', 'Elective'),
            ('GENERAL_ED', 'General Education'),
            ('PREREQUISITE', 'Prerequisite'),
        ]
    )
    
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='degree_requirements',
        null=True,
        blank=True,
        help_text=_('Specific course if applicable')
    )
    
    description = models.TextField(
        help_text=_('Description of the requirement')
    )
    
    credits_required = models.IntegerField(
        default=0,
        help_text=_('Number of credits required')
    )
    
    is_active = models.BooleanField(
        default=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'degree_requirements'
        verbose_name = _('Degree Requirement')
        verbose_name_plural = _('Degree Requirements')
    
    def __str__(self):
        return f"{self.major} - {self.requirement_type}: {self.description[:50]}"


class CourseRecommendation(models.Model):
    """Model for AI-generated course recommendations."""
    
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recommendations',
        limit_choices_to={'role': 'STUDENT'}
    )
    
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='recommendations'
    )
    
    score = models.FloatField(
        help_text=_('Recommendation score (0-1)')
    )
    
    reasoning = models.TextField(
        help_text=_('AI-generated explanation for the recommendation')
    )
    
    based_on = models.JSONField(
        default=dict,
        help_text=_('Factors used in generating this recommendation')
    )
    
    term = models.CharField(
        max_length=20,
        help_text=_('Recommended term')
    )
    
    year = models.IntegerField(
        help_text=_('Recommended year')
    )
    
    is_accepted = models.BooleanField(
        default=False,
        help_text=_('Whether student acted on this recommendation')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'course_recommendations'
        verbose_name = _('Course Recommendation')
        verbose_name_plural = _('Course Recommendations')
        ordering = ['-score', '-created_at']
    
    def __str__(self):
        return f"{self.student.username} -> {self.course.course_code} (score: {self.score})"


class RecommendationFeedback(models.Model):
    """Model to capture user feedback on recommendations for learning."""
    
    recommendation = models.ForeignKey(
        CourseRecommendation,
        on_delete=models.CASCADE,
        related_name='feedback'
    )
    
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recommendation_feedback'
    )
    
    rating = models.IntegerField(
        choices=[
            (1, 'Not Helpful'),
            (2, 'Somewhat Helpful'),
            (3, 'Helpful'),
            (4, 'Very Helpful'),
            (5, 'Extremely Helpful'),
        ],
        null=True,
        blank=True
    )
    
    comment = models.TextField(
        blank=True,
        help_text=_('User comment about the recommendation')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'recommendation_feedback'
        verbose_name = _('Recommendation Feedback')
        verbose_name_plural = _('Recommendation Feedback')
    
    def __str__(self):
        return f"Feedback from {self.student.username} on {self.recommendation.course.course_code}"

