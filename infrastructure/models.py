from django.db import models
from django.utils.translation import gettext_lazy as _
from authentication.models import User


class SystemLog(models.Model):
    """Model for system-wide logging and monitoring."""
    
    class Level(models.TextChoices):
        DEBUG = 'DEBUG', _('Debug')
        INFO = 'INFO', _('Info')
        WARNING = 'WARNING', _('Warning')
        ERROR = 'ERROR', _('Error')
        CRITICAL = 'CRITICAL', _('Critical')
    
    level = models.CharField(
        max_length=10,
        choices=Level.choices,
        default=Level.INFO
    )
    
    module = models.CharField(
        max_length=100,
        help_text=_('Module or component that generated the log')
    )
    
    message = models.TextField(
        help_text=_('Log message')
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='system_logs'
    )
    
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text=_('Additional context and metadata')
    )
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'system_logs'
        verbose_name = _('System Log')
        verbose_name_plural = _('System Logs')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['level']),
            models.Index(fields=['module']),
        ]
    
    def __str__(self):
        return f"[{self.level}] {self.module}: {self.message[:50]}"


class APIMetrics(models.Model):
    """Model for tracking API performance metrics."""
    
    endpoint = models.CharField(
        max_length=200,
        help_text=_('API endpoint path')
    )
    
    method = models.CharField(
        max_length=10,
        choices=[
            ('GET', 'GET'),
            ('POST', 'POST'),
            ('PUT', 'PUT'),
            ('PATCH', 'PATCH'),
            ('DELETE', 'DELETE'),
        ]
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='api_requests'
    )
    
    status_code = models.IntegerField(
        help_text=_('HTTP status code')
    )
    
    response_time = models.FloatField(
        help_text=_('Response time in milliseconds')
    )
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'api_metrics'
        verbose_name = _('API Metric')
        verbose_name_plural = _('API Metrics')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['endpoint']),
        ]
    
    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.status_code} ({self.response_time}ms)"

