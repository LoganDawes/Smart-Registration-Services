from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from courses.models import Course, CourseSection
from registration.models import Enrollment
from datetime import time
import json

User = get_user_model()


class RegistrationLayoutTestCase(TestCase):
    """Test that registration page layout matches catalog formatting."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='teststu',
            password='testpass',
            email='test@test.com',
            first_name='Test',
            last_name='Student'
        )
        self.user.role = User.Role.STUDENT
        self.user.save()
        
        # Create sample course and section
        self.course = Course.objects.create(
            course_code='CS101',
            title='Intro to CS',
            credits=3,
            department='CS',
            description='Test course'
        )
        self.section = CourseSection.objects.create(
            course=self.course,
            section_number='001',
            term='Fall',
            year=2024,
            max_enrollment=30,
            current_enrollment=0,
            meeting_days='MWF',
            start_time=time(9, 0),
            end_time=time(10, 0),
            is_available=True
        )
        
    def test_register_page_has_list_row_structure(self):
        """Verify register page uses list-row classes for consistent layout."""
        self.client.login(username='teststu', password='testpass')
        
        # Add a course to added courses
        session = self.client.session
        session['added_courses'] = [self.section.id]
        session.save()
        
        response = self.client.get(reverse('registration:register'))
        self.assertEqual(response.status_code, 200)
        
        # Check for list-row structure in template
        content = response.content.decode()
        self.assertIn('list-row', content)
        self.assertIn('list-row-course-code', content)
        self.assertIn('list-row-title', content)
        self.assertIn('list-row-credits', content)
        self.assertIn('list-row-actions', content)


class EnrollmentLogicTestCase(TestCase):
    """Test enrollment logic without unintended removal prompts."""
    
    def setUp(self):
        self.api_client = APIClient()
        self.user = User.objects.create_user(
            username='teststu',
            password='testpass',
            email='test@test.com',
            first_name='Test',
            last_name='Student'
        )
        self.user.role = User.Role.STUDENT
        self.user.save()
        
        self.course = Course.objects.create(
            course_code='CS101',
            title='Intro to CS',
            credits=3,
            department='CS',
            description='Test course'
        )
        self.section = CourseSection.objects.create(
            course=self.course,
            section_number='001',
            term='Fall',
            year=2024,
            max_enrollment=30,
            current_enrollment=0,
            meeting_days='MWF',
            start_time=time(9, 0),
            end_time=time(10, 0),
            is_available=True
        )
        
        self.api_client.force_authenticate(user=self.user)
    
    def test_register_single_without_prerequisite_check(self):
        """Test that registering for a course bypasses prerequisite validation."""
        # Create a course with prerequisites
        prereq_course = Course.objects.create(
            course_code='CS100',
            title='Pre CS',
            credits=3,
            department='CS',
            description='Prerequisite course'
        )
        self.course.prerequisites.add(prereq_course)
        
        # Try to enroll without having completed prerequisite
        response = self.api_client.post(
            '/api/registration-actions/enroll/',
            {'section_id': self.section.id},
            format='json'
        )
        
        # Should succeed (prerequisites are bypassed)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Enrollment.objects.filter(
            student=self.user,
            section=self.section
        ).exists())
    
    def test_enrollment_creates_record(self):
        """Test that enrollment creates proper enrollment record."""
        response = self.api_client.post(
            '/api/registration-actions/enroll/',
            {'section_id': self.section.id},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        enrollment = Enrollment.objects.get(student=self.user, section=self.section)
        self.assertEqual(enrollment.status, Enrollment.Status.ENROLLED)
    
    def test_duplicate_enrollment_prevented(self):
        """Test that duplicate enrollments are prevented."""
        # First enrollment
        self.api_client.post(
            '/api/registration-actions/enroll/',
            {'section_id': self.section.id},
            format='json'
        )
        
        # Try to enroll again
        response = self.api_client.post(
            '/api/registration-actions/enroll/',
            {'section_id': self.section.id},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already enrolled', response.data.get('error', '').lower())


class AddedCoursesManagementTestCase(TestCase):
    """Test added courses session management."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='teststu',
            password='testpass',
            email='test@test.com'
        )
        self.user.role = User.Role.STUDENT
        self.user.save()
        
        self.course = Course.objects.create(
            course_code='CS101',
            title='Intro to CS',
            credits=3,
            department='CS',
            description='Test course'
        )
        self.section = CourseSection.objects.create(
            course=self.course,
            section_number='001',
            term='Fall',
            year=2024,
            max_enrollment=30,
            current_enrollment=0,
            meeting_days='MWF',
            start_time=time(9, 0),
            end_time=time(10, 0),
            is_available=True
        )
        
        self.client.login(username='teststu', password='testpass')
    
    def test_add_to_added_courses(self):
        """Test adding a course to added courses list."""
        response = self.client.post(
            reverse('registration:add-to-added-courses'),
            json.dumps({'section_id': self.section.id}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        
        # Verify session contains the course
        session = self.client.session
        self.assertIn(self.section.id, session.get('added_courses', []))
    
    def test_remove_from_added_courses(self):
        """Test removing a course from added courses list."""
        # Add course first
        session = self.client.session
        session['added_courses'] = [self.section.id]
        session.save()
        
        # Remove it
        response = self.client.post(
            reverse('registration:remove-from-added-courses'),
            json.dumps({'section_id': self.section.id}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        
        # Verify session no longer contains the course
        session = self.client.session
        self.assertNotIn(self.section.id, session.get('added_courses', []))


class BulkRegistrationTestCase(TestCase):
    """Test bulk registration (confirm all) without prerequisite checks."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='teststu',
            password='testpass',
            email='test@test.com'
        )
        self.user.role = User.Role.STUDENT
        self.user.save()
        
        # Create courses with prerequisites
        self.prereq_course = Course.objects.create(
            course_code='CS100',
            title='Pre CS',
            credits=3,
            department='CS',
            description='Prerequisite'
        )
        
        self.course1 = Course.objects.create(
            course_code='CS101',
            title='Intro to CS',
            credits=3,
            department='CS',
            description='Test course 1'
        )
        self.course1.prerequisites.add(self.prereq_course)
        
        self.course2 = Course.objects.create(
            course_code='CS102',
            title='Data Structures',
            credits=3,
            department='CS',
            description='Test course 2'
        )
        
        self.section1 = CourseSection.objects.create(
            course=self.course1,
            section_number='001',
            term='Fall',
            year=2024,
            max_enrollment=30,
            current_enrollment=0,
            meeting_days='MWF',
            start_time=time(9, 0),
            end_time=time(10, 0),
            is_available=True
        )
        
        self.section2 = CourseSection.objects.create(
            course=self.course2,
            section_number='001',
            term='Fall',
            year=2024,
            max_enrollment=30,
            current_enrollment=0,
            meeting_days='TTH',
            start_time=time(11, 0),
            end_time=time(12, 30),
            is_available=True
        )
        
        self.client.login(username='teststu', password='testpass')
    
    def test_bulk_registration_bypasses_prerequisites(self):
        """Test that confirm all registration bypasses prerequisite checks."""
        response = self.client.post(
            reverse('registration:confirm-all'),
            json.dumps({
                'section_ids': [self.section1.id, self.section2.id]
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        
        # Both courses should be registered despite missing prerequisites
        self.assertEqual(data['registered'], 2)
        self.assertEqual(len(data['failed']), 0)
        
        # Verify enrollments
        enrollments = Enrollment.objects.filter(student=self.user)
        self.assertEqual(enrollments.count(), 2)

