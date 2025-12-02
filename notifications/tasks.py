from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Notification


@shared_task
def send_notification_email(notification_id):
    """Send email notification to user."""
    try:
        notification = Notification.objects.get(id=notification_id)
        
        if notification.send_email and not notification.email_sent:
            send_mail(
                subject=notification.title,
                message=notification.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notification.recipient.email],
                fail_silently=False,
            )
            
            notification.email_sent = True
            notification.sent_at = timezone.now()
            notification.save()
            
            return f"Email sent to {notification.recipient.email}"
    except Notification.DoesNotExist:
        return f"Notification {notification_id} not found"
    except Exception as e:
        return f"Error sending email: {str(e)}"


@shared_task
def send_bulk_notifications(user_ids, notification_type, title, message, send_email=False):
    """Send notifications to multiple users."""
    from authentication.models import User
    
    notifications_created = 0
    
    for user_id in user_ids:
        try:
            user = User.objects.get(id=user_id)
            notification = Notification.objects.create(
                recipient=user,
                notification_type=notification_type,
                title=title,
                message=message,
                send_email=send_email
            )
            
            if send_email:
                send_notification_email.delay(notification.id)
            
            notifications_created += 1
        except User.DoesNotExist:
            continue
    
    return f"Created {notifications_created} notifications"


@shared_task
def check_registration_deadlines():
    """Check for upcoming registration deadlines and send reminders."""
    # This would check for deadlines and create notifications
    # Implementation depends on how deadlines are stored
    pass


@shared_task
def check_meeting_reminders():
    """Check for upcoming advisor meetings and send reminders."""
    # This would check for scheduled meetings and create notifications
    # Implementation depends on how meetings are stored
    pass
