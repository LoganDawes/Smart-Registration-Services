from django.db import models
from django.utils.translation import gettext_lazy as _
from authentication.models import User
from planning.models import StudentPlan


class AdvisorAssignment(models.Model):
    """Model representing the assignment of an advisor to a student."""
    
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='advisor_assignments',
        limit_choices_to={'role': 'STUDENT'}
    )
    
    advisor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='student_assignments',
        limit_choices_to={'role': 'ADVISOR'}
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text=_('Whether this assignment is currently active')
    )
    
    assigned_at = models.DateTimeField(auto_now_add=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'advisor_assignments'
        verbose_name = _('Advisor Assignment')
        verbose_name_plural = _('Advisor Assignments')
        unique_together = [['student', 'advisor', 'is_active']]
    
    def __str__(self):
        return f"{self.student.username} -> {self.advisor.username}"


class ChatMessage(models.Model):
    """Model for real-time chat messages between students and advisors."""
    
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages'
    )
    
    plan = models.ForeignKey(
        StudentPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='chat_messages',
        help_text=_('Related student plan if message is about a specific plan')
    )
    
    message = models.TextField(
        help_text=_('Message content')
    )
    
    is_read = models.BooleanField(
        default=False
    )
    
    sent_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'chat_messages'
        verbose_name = _('Chat Message')
        verbose_name_plural = _('Chat Messages')
        ordering = ['sent_at']
    
    def __str__(self):
        return f"{self.sender.username} -> {self.recipient.username}: {self.message[:50]}"


class PlanComment(models.Model):
    """Model for advisor comments and annotations on student plans."""
    
    plan = models.ForeignKey(
        StudentPlan,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    
    advisor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='plan_comments',
        limit_choices_to={'role': 'ADVISOR'}
    )
    
    comment = models.TextField(
        help_text=_('Advisor comment')
    )
    
    requires_change = models.BooleanField(
        default=False,
        help_text=_('Whether this comment requires the student to make changes')
    )
    
    is_resolved = models.BooleanField(
        default=False,
        help_text=_('Whether the comment has been addressed')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'plan_comments'
        verbose_name = _('Plan Comment')
        verbose_name_plural = _('Plan Comments')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.advisor.username} on {self.plan}"

