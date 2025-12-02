from django.db import models
from django.utils.translation import gettext_lazy as _
from authentication.models import User


class Notification(models.Model):
    """Model for system notifications to users."""
    
    class Type(models.TextChoices):
        REGISTRATION_DEADLINE = 'REGISTRATION_DEADLINE', _('Registration Deadline')
        MEETING_REMINDER = 'MEETING_REMINDER', _('Meeting Reminder')
        SCHEDULE_CHANGE = 'SCHEDULE_CHANGE', _('Schedule Change')
        ADVISOR_ACTION = 'ADVISOR_ACTION', _('Advisor Action')
        PLAN_APPROVED = 'PLAN_APPROVED', _('Plan Approved')
        PLAN_REJECTED = 'PLAN_REJECTED', _('Plan Rejected')
        NEW_MESSAGE = 'NEW_MESSAGE', _('New Message')
        ENROLLMENT_CONFIRMED = 'ENROLLMENT_CONFIRMED', _('Enrollment Confirmed')
        WAITLIST_UPDATE = 'WAITLIST_UPDATE', _('Waitlist Update')
        GENERAL = 'GENERAL', _('General')
    
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    notification_type = models.CharField(
        max_length=30,
        choices=Type.choices
    )
    
    title = models.CharField(
        max_length=200,
        help_text=_('Notification title')
    )
    
    message = models.TextField(
        help_text=_('Notification message content')
    )
    
    link = models.URLField(
        blank=True,
        help_text=_('Link to relevant page')
    )
    
    is_read = models.BooleanField(
        default=False
    )
    
    is_sent = models.BooleanField(
        default=False,
        help_text=_('Whether notification has been delivered')
    )
    
    send_email = models.BooleanField(
        default=False,
        help_text=_('Whether to send email notification')
    )
    
    email_sent = models.BooleanField(
        default=False
    )
    
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text=_('Additional notification metadata')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'notifications'
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification_type} for {self.recipient.username}: {self.title}"


class NotificationPreference(models.Model):
    """Model for user notification preferences."""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='notification_preference'
    )
    
    email_notifications = models.BooleanField(
        default=True,
        help_text=_('Receive notifications via email')
    )
    
    push_notifications = models.BooleanField(
        default=True,
        help_text=_('Receive push notifications')
    )
    
    registration_deadlines = models.BooleanField(
        default=True
    )
    
    meeting_reminders = models.BooleanField(
        default=True
    )
    
    schedule_changes = models.BooleanField(
        default=True
    )
    
    advisor_actions = models.BooleanField(
        default=True
    )
    
    new_messages = models.BooleanField(
        default=True
    )
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_preferences'
        verbose_name = _('Notification Preference')
        verbose_name_plural = _('Notification Preferences')
    
    def __str__(self):
        return f"Preferences for {self.user.username}"

