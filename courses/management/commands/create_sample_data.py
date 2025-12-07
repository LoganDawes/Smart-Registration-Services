"""
Management command to create sample course data for testing and demonstration.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from datetime import time
from courses.models import Course, CourseSection
from planning.models import StudentPlan, PlannedCourse
from registration.models import Enrollment

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample course data for testing and demonstration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing course data before creating new data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing course data...')
            CourseSection.objects.all().delete()
            Course.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Cleared existing data'))

        self.stdout.write('Creating sample courses...')
        
        # Create Computer Science courses
        cs101 = Course.objects.create(
            course_code='CS101',
            title='Introduction to Computer Science',
            description='Fundamental concepts of computer science including programming basics, algorithms, and data structures.',
            credits=3,
            department='Computer Science',
            level='FRESHMAN',
            is_active=True
        )
        
        cs201 = Course.objects.create(
            course_code='CS201',
            title='Data Structures and Algorithms',
            description='Advanced data structures, algorithm design and analysis, sorting and searching algorithms.',
            credits=4,
            department='Computer Science',
            level='SOPHOMORE',
            is_active=True
        )
        cs201.prerequisites.add(cs101)
        
        cs301 = Course.objects.create(
            course_code='CS301',
            title='Database Systems',
            description='Database design, SQL, normalization, transactions, and database management systems.',
            credits=3,
            department='Computer Science',
            level='JUNIOR',
            is_active=True
        )
        cs301.prerequisites.add(cs201)
        
        cs302 = Course.objects.create(
            course_code='CS302',
            title='Software Engineering',
            description='Software development lifecycle, design patterns, testing, and project management.',
            credits=3,
            department='Computer Science',
            level='JUNIOR',
            is_active=True
        )
        cs302.prerequisites.add(cs201)
        
        # Create Mathematics courses
        math101 = Course.objects.create(
            course_code='MATH101',
            title='Calculus I',
            description='Limits, derivatives, integrals, and applications of calculus.',
            credits=4,
            department='Mathematics',
            level='FRESHMAN',
            is_active=True
        )
        
        math201 = Course.objects.create(
            course_code='MATH201',
            title='Calculus II',
            description='Advanced integration techniques, series, and multivariable calculus.',
            credits=4,
            department='Mathematics',
            level='SOPHOMORE',
            is_active=True
        )
        math201.prerequisites.add(math101)
        
        math301 = Course.objects.create(
            course_code='MATH301',
            title='Linear Algebra',
            description='Vector spaces, matrices, linear transformations, eigenvalues and eigenvectors.',
            credits=3,
            department='Mathematics',
            level='JUNIOR',
            is_active=True
        )
        math301.prerequisites.add(math201)
        
        # Create English courses
        eng101 = Course.objects.create(
            course_code='ENG101',
            title='Composition and Rhetoric',
            description='Academic writing, critical thinking, and research skills.',
            credits=3,
            department='English',
            level='FRESHMAN',
            is_active=True
        )
        
        eng201 = Course.objects.create(
            course_code='ENG201',
            title='World Literature',
            description='Survey of world literature from ancient to modern times.',
            credits=3,
            department='English',
            level='SOPHOMORE',
            is_active=True
        )
        
        self.stdout.write(self.style.SUCCESS(f'Created {Course.objects.count()} courses'))
        
        # Create course sections for Fall 2024
        self.stdout.write('Creating course sections for Fall 2024...')
        
        # Get or create an instructor
        instructor, created = User.objects.get_or_create(
            username='instructor1',
            defaults={
                'email': 'instructor1@example.com',
                'first_name': 'John',
                'last_name': 'Smith',
                'role': 'ADVISOR'
            }
        )
        
        sections_data = [
            # CS courses
            (cs101, '001', 'Fall', 2024, 'MWF', time(9, 0), time(9, 50), 'CS 101', 30),
            (cs101, '002', 'Fall', 2024, 'TTH', time(10, 30), time(11, 45), 'CS 102', 30),
            (cs201, '001', 'Fall', 2024, 'MWF', time(11, 0), time(11, 50), 'CS 201', 25),
            (cs201, '002', 'Fall', 2024, 'TTH', time(13, 0), time(14, 15), 'CS 202', 25),
            (cs301, '001', 'Fall', 2024, 'MWF', time(14, 0), time(14, 50), 'CS 301', 25),
            (cs302, '001', 'Fall', 2024, 'TTH', time(15, 30), time(16, 45), 'CS 302', 25),
            
            # Math courses
            (math101, '001', 'Fall', 2024, 'MWF', time(8, 0), time(8, 50), 'MATH 101', 35),
            (math101, '002', 'Fall', 2024, 'TTH', time(9, 0), time(10, 15), 'MATH 102', 35),
            (math201, '001', 'Fall', 2024, 'MWF', time(10, 0), time(10, 50), 'MATH 201', 30),
            (math301, '001', 'Fall', 2024, 'TTH', time(11, 30), time(12, 45), 'MATH 301', 25),
            
            # English courses
            (eng101, '001', 'Fall', 2024, 'MWF', time(13, 0), time(13, 50), 'ENG 101', 25),
            (eng101, '002', 'Fall', 2024, 'TTH', time(14, 30), time(15, 45), 'ENG 102', 25),
            (eng201, '001', 'Fall', 2024, 'MWF', time(15, 0), time(15, 50), 'ENG 201', 25),
        ]
        
        for course, section_num, term, year, days, start, end, location, max_enroll in sections_data:
            CourseSection.objects.create(
                course=course,
                section_number=section_num,
                term=term,
                year=year,
                instructor=instructor,
                max_enrollment=max_enroll,
                current_enrollment=0,
                location=location,
                meeting_days=days,
                start_time=start,
                end_time=end,
                is_available=True
            )
        
        self.stdout.write(self.style.SUCCESS(f'Created {CourseSection.objects.count()} course sections'))
        
        # Create sections for Spring 2025
        self.stdout.write('Creating course sections for Spring 2025...')
        
        spring_sections = [
            (cs101, '001', 'Spring', 2025, 'MWF', time(9, 0), time(9, 50), 'CS 101', 30),
            (cs201, '001', 'Spring', 2025, 'MWF', time(11, 0), time(11, 50), 'CS 201', 25),
            (cs301, '001', 'Spring', 2025, 'TTH', time(13, 0), time(14, 15), 'CS 301', 25),
            (math101, '001', 'Spring', 2025, 'MWF', time(8, 0), time(8, 50), 'MATH 101', 35),
            (math201, '001', 'Spring', 2025, 'TTH', time(10, 30), time(11, 45), 'MATH 201', 30),
            (eng101, '001', 'Spring', 2025, 'MWF', time(13, 0), time(13, 50), 'ENG 101', 25),
        ]
        
        for course, section_num, term, year, days, start, end, location, max_enroll in spring_sections:
            CourseSection.objects.create(
                course=course,
                section_number=section_num,
                term=term,
                year=year,
                instructor=instructor,
                max_enrollment=max_enroll,
                current_enrollment=0,
                location=location,
                meeting_days=days,
                start_time=start,
                end_time=end,
                is_available=True
            )
        
        self.stdout.write(self.style.SUCCESS(
            f'Total sections created: {CourseSection.objects.count()}'
        ))
        
        self.stdout.write(self.style.SUCCESS('Sample data creation completed!'))
        self.stdout.write(
            self.style.WARNING(
                '\nNote: You can now access the course catalog at /courses/catalog/'
            )
        )
