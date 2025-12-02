from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import time
from authentication.models import User
from courses.models import Course, CourseSection


class Command(BaseCommand):
    help = 'Populate the database with sample courses and sections'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')
        
        # Create sample courses
        courses_data = [
            {
                'course_code': 'CS101',
                'title': 'Introduction to Computer Science',
                'description': 'Fundamental concepts of computer science including programming, algorithms, and data structures.',
                'credits': 3,
                'department': 'Computer Science',
                'level': 'FRESHMAN',
            },
            {
                'course_code': 'CS201',
                'title': 'Data Structures and Algorithms',
                'description': 'Advanced study of data structures and algorithm design and analysis.',
                'credits': 3,
                'department': 'Computer Science',
                'level': 'SOPHOMORE',
            },
            {
                'course_code': 'CS301',
                'title': 'Database Systems',
                'description': 'Design and implementation of database systems, SQL, and database management.',
                'credits': 3,
                'department': 'Computer Science',
                'level': 'JUNIOR',
            },
            {
                'course_code': 'MATH101',
                'title': 'Calculus I',
                'description': 'Differential and integral calculus with applications.',
                'credits': 4,
                'department': 'Mathematics',
                'level': 'FRESHMAN',
            },
            {
                'course_code': 'MATH201',
                'title': 'Calculus II',
                'description': 'Continuation of Calculus I covering advanced integration and series.',
                'credits': 4,
                'department': 'Mathematics',
                'level': 'SOPHOMORE',
            },
            {
                'course_code': 'ENG101',
                'title': 'English Composition',
                'description': 'Development of writing skills through practice in composing and revising essays.',
                'credits': 3,
                'department': 'English',
                'level': 'FRESHMAN',
            },
            {
                'course_code': 'PHYS101',
                'title': 'General Physics I',
                'description': 'Introduction to mechanics, heat, and sound.',
                'credits': 4,
                'department': 'Physics',
                'level': 'FRESHMAN',
            },
            {
                'course_code': 'CHEM101',
                'title': 'General Chemistry',
                'description': 'Fundamental principles of chemistry including atomic structure and chemical bonding.',
                'credits': 4,
                'department': 'Chemistry',
                'level': 'FRESHMAN',
            },
        ]
        
        created_courses = {}
        for course_data in courses_data:
            course, created = Course.objects.get_or_create(
                course_code=course_data['course_code'],
                defaults=course_data
            )
            created_courses[course_data['course_code']] = course
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created course: {course.course_code}'))
            else:
                self.stdout.write(f'Course already exists: {course.course_code}')
        
        # Set up prerequisites
        if 'CS101' in created_courses and 'CS201' in created_courses:
            created_courses['CS201'].prerequisites.add(created_courses['CS101'])
            self.stdout.write('Added CS101 as prerequisite for CS201')
        
        if 'CS201' in created_courses and 'CS301' in created_courses:
            created_courses['CS301'].prerequisites.add(created_courses['CS201'])
            self.stdout.write('Added CS201 as prerequisite for CS301')
        
        if 'MATH101' in created_courses and 'MATH201' in created_courses:
            created_courses['MATH201'].prerequisites.add(created_courses['MATH101'])
            self.stdout.write('Added MATH101 as prerequisite for MATH201')
        
        # Create sample instructor
        instructor, created = User.objects.get_or_create(
            username='prof_smith',
            defaults={
                'email': 'smith@example.edu',
                'first_name': 'John',
                'last_name': 'Smith',
                'role': User.Role.ADVISOR,
            }
        )
        if created:
            instructor.set_password('password123')
            instructor.save()
            self.stdout.write(self.style.SUCCESS('Created instructor: prof_smith'))
        
        # Create course sections
        sections_data = [
            {
                'course': created_courses['CS101'],
                'section_number': '001',
                'term': 'Fall',
                'year': 2024,
                'instructor': instructor,
                'max_enrollment': 30,
                'location': 'CS Building 101',
                'meeting_days': 'MWF',
                'start_time': time(9, 0),
                'end_time': time(10, 0),
            },
            {
                'course': created_courses['CS101'],
                'section_number': '002',
                'term': 'Fall',
                'year': 2024,
                'instructor': instructor,
                'max_enrollment': 30,
                'location': 'CS Building 102',
                'meeting_days': 'TTH',
                'start_time': time(11, 0),
                'end_time': time(12, 30),
            },
            {
                'course': created_courses['CS201'],
                'section_number': '001',
                'term': 'Fall',
                'year': 2024,
                'instructor': instructor,
                'max_enrollment': 25,
                'location': 'CS Building 201',
                'meeting_days': 'MWF',
                'start_time': time(10, 0),
                'end_time': time(11, 0),
            },
            {
                'course': created_courses['MATH101'],
                'section_number': '001',
                'term': 'Fall',
                'year': 2024,
                'instructor': instructor,
                'max_enrollment': 35,
                'location': 'Math Building 101',
                'meeting_days': 'MWF',
                'start_time': time(8, 0),
                'end_time': time(9, 0),
            },
            {
                'course': created_courses['ENG101'],
                'section_number': '001',
                'term': 'Fall',
                'year': 2024,
                'instructor': instructor,
                'max_enrollment': 20,
                'location': 'English Building 101',
                'meeting_days': 'TTH',
                'start_time': time(14, 0),
                'end_time': time(15, 30),
            },
        ]
        
        for section_data in sections_data:
            section, created = CourseSection.objects.get_or_create(
                course=section_data['course'],
                section_number=section_data['section_number'],
                term=section_data['term'],
                year=section_data['year'],
                defaults=section_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(
                    f'Created section: {section.course.course_code}-{section.section_number}'
                ))
        
        self.stdout.write(self.style.SUCCESS('\nSample data created successfully!'))
        self.stdout.write('You can now:')
        self.stdout.write('  - Browse courses at /api/courses/')
        self.stdout.write('  - View sections at /api/sections/')
        self.stdout.write('  - Access admin at /admin/ (username: admin)')
