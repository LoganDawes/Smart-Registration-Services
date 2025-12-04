from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom User model with role-based permissions for the Smart Registration System.
    Supports three types of users: Students, Advisors, and Registrar staff.
    """
    class Role(models.TextChoices):
        STUDENT = 'STUDENT', _('Student')
        ADVISOR = 'ADVISOR', _('Advisor')
        REGISTRAR = 'REGISTRAR', _('Registrar')
    
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT,
        help_text=_('User role in the system')
    )
    
    student_id = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        unique=True,
        help_text=_('Unique student identification number')
    )
    
    advisor_id = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        unique=True,
        help_text=_('Unique advisor identification number')
    )
    
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        help_text=_('Contact phone number')
    )
    
    department = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('Department affiliation')
    )
    
    major = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('Student major (for students)')
    )
    
    year_of_study = models.IntegerField(
        null=True,
        blank=True,
        help_text=_('Year of study (1-4 for undergrad, 5+ for grad)')
    )
    
    notification_preferences = models.JSONField(
        default=dict,
        blank=True,
        help_text=_('User notification preferences')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = _('User')
        verbose_name_plural = _('Users')
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    def is_student(self):
        return self.role == self.Role.STUDENT
    
    def is_advisor(self):
        return self.role == self.Role.ADVISOR
    
    def is_registrar(self):
        return self.role == self.Role.REGISTRAR

