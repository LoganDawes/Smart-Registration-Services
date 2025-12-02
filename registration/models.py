from django.db import models
from django.utils.translation import gettext_lazy as _
from authentication.models import User
from courses.models import CourseSection
from planning.models import StudentPlan


class Enrollment(models.Model):
    """Model representing a student's enrollment in a course section."""
    
    class Status(models.TextChoices):
        ENROLLED = 'ENROLLED', _('Enrolled')
        WAITLISTED = 'WAITLISTED', _('Waitlisted')
        DROPPED = 'DROPPED', _('Dropped')
    
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='enrollments',
        limit_choices_to={'role': 'STUDENT'}
    )
    
    section = models.ForeignKey(
        CourseSection,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.ENROLLED
    )
    
    grade = models.CharField(
        max_length=5,
        blank=True,
        help_text=_('Final grade for the course')
    )
    
    enrolled_at = models.DateTimeField(auto_now_add=True)
    dropped_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'enrollments'
        verbose_name = _('Enrollment')
        verbose_name_plural = _('Enrollments')
        unique_together = [['student', 'section']]
        ordering = ['-enrolled_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.section} ({self.status})"


class RegistrationRequest(models.Model):
    """Model representing a registration request that requires advisor approval."""
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending Approval')
        APPROVED = 'APPROVED', _('Approved')
        REJECTED = 'REJECTED', _('Rejected')
        COMPLETED = 'COMPLETED', _('Completed')
    
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='registration_requests',
        limit_choices_to={'role': 'STUDENT'}
    )
    
    advisor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_requests',
        limit_choices_to={'role': 'ADVISOR'}
    )
    
    plan = models.ForeignKey(
        StudentPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='registration_requests',
        help_text=_('Associated student plan if registering from a plan')
    )
    
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING
    )
    
    notes = models.TextField(
        blank=True,
        help_text=_('Student notes for this registration request')
    )
    
    advisor_comments = models.TextField(
        blank=True,
        help_text=_('Advisor comments on this request')
    )
    
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'registration_requests'
        verbose_name = _('Registration Request')
        verbose_name_plural = _('Registration Requests')
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.status}"


class RegistrationLog(models.Model):
    """Model to log all registration actions for audit purposes."""
    
    class Action(models.TextChoices):
        REGISTER = 'REGISTER', _('Register')
        DROP = 'DROP', _('Drop')
        WAITLIST = 'WAITLIST', _('Add to Waitlist')
        APPROVE = 'APPROVE', _('Approve Request')
        REJECT = 'REJECT', _('Reject Request')
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='registration_logs'
    )
    
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logs'
    )
    
    request = models.ForeignKey(
        RegistrationRequest,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logs'
    )
    
    action = models.CharField(
        max_length=10,
        choices=Action.choices
    )
    
    details = models.JSONField(
        default=dict,
        help_text=_('Additional details about the action')
    )
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'registration_logs'
        verbose_name = _('Registration Log')
        verbose_name_plural = _('Registration Logs')
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user} - {self.action} at {self.timestamp}"

