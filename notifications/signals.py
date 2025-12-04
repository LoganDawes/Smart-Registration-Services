from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
import datetime

from courses.models import CourseSection
from registration.models import Enrollment
from .models import Notification, NotificationPreference
from . import tasks


@receiver(pre_save, sender=CourseSection)
def cache_old_course_section(sender, instance, **kwargs):
    """Cache the old CourseSection on the instance before save so we can compare in post_save."""
    if not instance.pk:
        instance._old_course_section = None
        return

    try:
        old = CourseSection.objects.get(pk=instance.pk)
        instance._old_course_section = old
    except CourseSection.DoesNotExist:
        instance._old_course_section = None


@receiver(post_save, sender=CourseSection)
def handle_course_section_update(sender, instance, created, **kwargs):
    """Detect schedule-related changes and create notifications for enrolled students."""
    # Only care about updates
    if created:
        return

    old = getattr(instance, '_old_course_section', None)
    if not old:
        # Could not determine previous state; skip
        return

    changed_fields = []
    # fields to watch
    watched = ['meeting_days', 'start_time', 'end_time', 'location', 'instructor_id']

    for field in watched:
        old_val = getattr(old, field, None)
        new_val = getattr(instance, field, None)
        if old_val != new_val:
            changed_fields.append((field, old_val, new_val))

    if not changed_fields:
        return

    # Format a message summarizing changes
    changes_text = []
    for field, old_val, new_val in changed_fields:
        # For instructor_id, try to show username if possible
        if field == 'instructor_id':
            old_disp = getattr(old.instructor, 'username', None) if old.instructor else None
            new_disp = getattr(instance.instructor, 'username', None) if instance.instructor else None
        else:
            old_disp = old_val
            new_disp = new_val

        changes_text.append(f"{field.replace('_', ' ').title()}: {old_disp}  {new_disp}")

    title = f"Schedule change: {instance.course.course_code} {instance.section_number}"
    message = "The following changes were made to your course section:\n" + "\n".join(changes_text)

    # Notify all enrolled students (status ENROLLED)
    enrollments = Enrollment.objects.filter(section=instance, status=Enrollment.Status.ENROLLED).select_related('student')

    for enrollment in enrollments:
        user = enrollment.student

        # Check user preferences (NotificationPreference)  default to allow
        try:
            pref = user.notification_preference
        except NotificationPreference.DoesNotExist:
            pref = None

        if pref and not pref.schedule_changes:
            continue

        send_email = True if (pref is None or pref.email_notifications) else False

        # Serialize change values for JSON storage
        def _serialize(val):
            if val is None:
                return None
            if isinstance(val, (datetime.datetime, datetime.date, datetime.time)):
                return val.isoformat()
            # For model instances like User, prefer username
            if hasattr(val, 'username'):
                return getattr(val, 'username')
            try:
                return str(val)
            except Exception:
                return None

        notif = Notification.objects.create(
            recipient=user,
            notification_type=Notification.Type.SCHEDULE_CHANGE,
            title=title,
            message=message,
            link='',
            send_email=send_email,
            metadata={
                'section_id': instance.id,
                'changes': [{
                    'field': f,
                    'old': _serialize(o),
                    'new': _serialize(n)
                } for f, o, n in changed_fields]
            }
        )

        # Queue email send if requested
        if send_email:
            try:
                tasks.send_notification_email.delay(notif.id)
            except Exception:
                # If Celery not configured in test environment, ignore
                pass
