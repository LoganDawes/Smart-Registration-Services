from django.db import models
from django.utils.translation import gettext_lazy as _
from authentication.models import User
from courses.models import Course, CourseSection


class StudentPlan(models.Model):
    """Model representing a student's course planning schedule."""
    
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', _('Draft')
        SUBMITTED = 'SUBMITTED', _('Submitted for Review')
        APPROVED = 'APPROVED', _('Approved')
        REJECTED = 'REJECTED', _('Rejected')
    
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='plans',
        limit_choices_to={'role': 'STUDENT'}
    )
    
    advisor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='advised_plans',
        limit_choices_to={'role': 'ADVISOR'}
    )
    
    term = models.CharField(
        max_length=20,
        help_text=_('Academic term for this plan')
    )
    
    year = models.IntegerField(
        help_text=_('Academic year for this plan')
    )
    
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT
    )
    
    name = models.CharField(
        max_length=200,
        help_text=_('Plan name/description')
    )
    
    notes = models.TextField(
        blank=True,
        help_text=_('Student notes about this plan')
    )
    
    advisor_comments = models.TextField(
        blank=True,
        help_text=_('Advisor comments on this plan')
    )
    
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'student_plans'
        verbose_name = _('Student Plan')
        verbose_name_plural = _('Student Plans')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.name} ({self.term} {self.year})"


class PlannedCourse(models.Model):
    """Model representing a course in a student's plan."""
    
    plan = models.ForeignKey(
        StudentPlan,
        on_delete=models.CASCADE,
        related_name='planned_courses'
    )
    
    section = models.ForeignKey(
        CourseSection,
        on_delete=models.CASCADE,
        related_name='plans'
    )
    
    priority = models.IntegerField(
        default=0,
        help_text=_('Priority ranking for this course')
    )
    
    notes = models.TextField(
        blank=True,
        help_text=_('Notes about this course in the plan')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'planned_courses'
        verbose_name = _('Planned Course')
        verbose_name_plural = _('Planned Courses')
        unique_together = [['plan', 'section']]
    
    def __str__(self):
        return f"{self.plan.student.username} - {self.section}"


class ScheduleConflict(models.Model):
    """Model to track schedule conflicts in student plans."""
    
    plan = models.ForeignKey(
        StudentPlan,
        on_delete=models.CASCADE,
        related_name='conflicts'
    )
    
    course1 = models.ForeignKey(
        PlannedCourse,
        on_delete=models.CASCADE,
        related_name='conflicts_as_first'
    )
    
    course2 = models.ForeignKey(
        PlannedCourse,
        on_delete=models.CASCADE,
        related_name='conflicts_as_second'
    )
    
    conflict_type = models.CharField(
        max_length=50,
        choices=[
            ('TIME_OVERLAP', 'Time Overlap'),
            ('PREREQUISITE_MISSING', 'Missing Prerequisite'),
        ],
        default='TIME_OVERLAP'
    )
    
    description = models.TextField(
        help_text=_('Description of the conflict')
    )
    
    is_resolved = models.BooleanField(
        default=False
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'schedule_conflicts'
        verbose_name = _('Schedule Conflict')
        verbose_name_plural = _('Schedule Conflicts')
    
    def __str__(self):
        return f"Conflict: {self.course1.section} vs {self.course2.section}"

