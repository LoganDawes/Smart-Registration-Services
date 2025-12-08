from django.shortcuts import render
from django.views.generic import TemplateView
from .models import Notification


class NotificationsView(TemplateView):
    """Notifications page view."""
    template_name = 'notifications/notifications_new.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get notifications for the current user if authenticated
        if self.request.user.is_authenticated:
            # Get all notifications for the user
            all_notifications = Notification.objects.filter(
                recipient=self.request.user
            ).order_by('-created_at')
            
            # Separate unread and read notifications
            context['unread_notifications'] = all_notifications.filter(is_read=False)
            context['read_notifications'] = all_notifications.filter(is_read=True)
            context['total_notifications'] = all_notifications.count()
            context['unread_count'] = all_notifications.filter(is_read=False).count()
        else:
            context['unread_notifications'] = []
            context['read_notifications'] = []
            context['total_notifications'] = 0
            context['unread_count'] = 0
        
        return context


notifications = NotificationsView.as_view()


from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
import json


@login_required
def send_test_notification(request):
    """Send a test notification to the current user."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    data = json.loads(request.body)
    notification_type = data.get('notification_type', 'GENERAL')
    
    # Define test notification content based on type
    notification_content = {
        'REGISTRATION_DEADLINE': {
            'title': 'Registration Deadline Approaching',
            'message': 'The registration deadline for Spring 2025 is approaching. Please complete your registration by December 15, 2024.'
        },
        'MEETING_REMINDER': {
            'title': 'Advisor Meeting Reminder',
            'message': 'You have a scheduled meeting with your advisor tomorrow at 2:00 PM in Office 301.'
        },
        'SCHEDULE_CHANGE': {
            'title': 'Schedule Change Alert',
            'message': 'CS301 Section 001 has been moved to a new time: TTH 10:00 AM - 11:30 AM, Room 204.'
        },
        'PLAN_APPROVED': {
            'title': 'Plan Approved',
            'message': 'Your Fall 2024 schedule plan has been approved by your advisor. You may now proceed with registration.'
        },
        'ENROLLMENT_CONFIRMED': {
            'title': 'Enrollment Confirmed',
            'message': 'You have been successfully enrolled in CS101 Section 001 for Spring 2025.'
        },
        'GENERAL': {
            'title': 'System Notice',
            'message': 'This is a test notification from the Smart Registration System.'
        }
    }
    
    content = notification_content.get(notification_type, notification_content['GENERAL'])
    
    # Create notification
    notification = Notification.objects.create(
        recipient=request.user,
        notification_type=notification_type,
        title=content['title'],
        message=content['message'],
        is_sent=True,
        sent_at=timezone.now()
    )
    
    return JsonResponse({
        'success': True,
        'notification_id': notification.id,
        'message': 'Test notification sent'
    })


@login_required
def mark_notification_read(request, notification_id):
    """Mark a notification as read."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        notification = Notification.objects.get(
            id=notification_id,
            recipient=request.user
        )
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Notification marked as read'
        })
    except Notification.DoesNotExist:
        return JsonResponse({
            'error': 'Notification not found'
        }, status=404)
