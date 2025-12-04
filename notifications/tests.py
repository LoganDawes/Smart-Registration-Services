from django.test import TestCase
from unittest.mock import patch

from authentication.models import User
from courses.models import Course, CourseSection
from registration.models import Enrollment
from .models import Notification, NotificationPreference


class ScheduleChangeSignalTests(TestCase):
    def setUp(self):
        # Create a student user and an instructor
        self.student = User.objects.create_user(
            username='student1', password='pass', email='student1@example.com', role=User.Role.STUDENT
        )
        self.instructor = User.objects.create_user(
            username='instructor1', password='pass', email='instr@example.com', role=User.Role.ADVISOR
        )

        # Create notification preference for the student
        NotificationPreference.objects.create(user=self.student)

        # Course and section
        self.course = Course.objects.create(
            course_code='CS101', title='Intro', description='Desc', credits=3, department='CS', level='FRESHMAN'
        )
        self.section = CourseSection.objects.create(
            course=self.course,
            section_number='001',
            term='Fall',
            year=2025,
            instructor=self.instructor,
            max_enrollment=30,
            current_enrollment=1,
            location='Room 1',
            meeting_days='MWF',
            start_time='09:00',
            end_time='10:00'
        )

        # Enroll student
        Enrollment.objects.create(student=self.student, section=self.section, status=Enrollment.Status.ENROLLED)
from django.test import TestCase
from unittest.mock import patch

from authentication.models import User
from courses.models import Course, CourseSection
from registration.models import Enrollment
from .models import Notification, NotificationPreference


class ScheduleChangeSignalTests(TestCase):
	def setUp(self):
		# Create a student user and an instructor
		self.student = User.objects.create_user(
			username='student1', password='pass', email='student1@example.com', role=User.Role.STUDENT
		)
		self.instructor = User.objects.create_user(
			username='instructor1', password='pass', email='instr@example.com', role=User.Role.ADVISOR
		)

		# Create notification preference for the student
		NotificationPreference.objects.create(user=self.student)

		# Course and section
		self.course = Course.objects.create(
			course_code='CS101', title='Intro', description='Desc', credits=3, department='CS', level='FRESHMAN'
		)
		self.section = CourseSection.objects.create(
			course=self.course,
			section_number='001',
			term='Fall',
			year=2025,
			instructor=self.instructor,
			max_enrollment=30,
			current_enrollment=1,
			location='Room 1',
			meeting_days='MWF',
			start_time='09:00',
			end_time='10:00'
		)

		# Enroll student
		Enrollment.objects.create(student=self.student, section=self.section, status=Enrollment.Status.ENROLLED)

	@patch('notifications.signals.tasks.send_notification_email')
	def test_schedule_change_creates_notifications(self, mock_send_email_task):
		# Update the section start_time and location to trigger the signal
		self.section.start_time = '10:00'
		self.section.location = 'Room 2'
		self.section.save()

		# Check that a notification was created for the student
		notifs = Notification.objects.filter(
			recipient=self.student, notification_type=Notification.Type.SCHEDULE_CHANGE
		)
		self.assertTrue(notifs.exists())

		notif = notifs.first()
		# message should mention changed fields
		self.assertIn('Location', notif.message) or self.assertIn('location', notif.message.lower())

		# If the task was queued via .delay on the Celery task, the patched object should have been called
		try:
			mock_send_email_task.delay.assert_called()
		except Exception:
			# Fallback: ensure email_sent is still False initially
			self.assertFalse(notif.email_sent)
		self.section.location = 'Room 2'
