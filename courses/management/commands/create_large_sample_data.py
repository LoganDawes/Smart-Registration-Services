"""
Management command to create a large set of sample course data for testing and demonstration.
Creates 60+ courses across multiple departments with varied schedules, prerequisites, and patterns.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from datetime import time
from courses.models import Course, CourseSection
from planning.models import StudentPlan, PlannedCourse
from registration.models import Enrollment

User = get_user_model()


class Command(BaseCommand):
    help = 'Create large sample course dataset (60+ courses) for testing and demonstration'

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

        self.stdout.write('Creating large sample course dataset...')
        
        # Dictionary to store courses for prerequisites
        courses = {}
        
        # Get or create instructors
        instructors = {}
        instructor_names = [
            ('john.smith', 'John', 'Smith'),
            ('jane.doe', 'Jane', 'Doe'),
            ('robert.johnson', 'Robert', 'Johnson'),
            ('maria.garcia', 'Maria', 'Garcia'),
            ('david.brown', 'David', 'Brown'),
            ('sarah.wilson', 'Sarah', 'Wilson'),
            ('michael.lee', 'Michael', 'Lee'),
            ('emily.taylor', 'Emily', 'Taylor'),
        ]
        
        for username, first_name, last_name in instructor_names:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': f'{username}@university.edu',
                    'role': 'INSTRUCTOR'
                }
            )
            instructors[username] = user
        
        instructor_list = list(instructors.values())
        
        # Computer Science Courses (15 courses)
        cs_courses = [
            ('CS101', 'Introduction to Computer Science', 'Fundamental concepts of computer science including programming basics, algorithms, and data structures.', 3, 'FRESHMAN', []),
            ('CS102', 'Programming Fundamentals', 'Basic programming concepts, control structures, functions, and object-oriented programming.', 3, 'FRESHMAN', []),
            ('CS201', 'Data Structures and Algorithms', 'Advanced data structures, algorithm design and analysis, sorting and searching algorithms.', 4, 'SOPHOMORE', ['CS101']),
            ('CS202', 'Computer Organization', 'Digital logic, computer architecture, assembly language, and system performance.', 3, 'SOPHOMORE', ['CS101']),
            ('CS203', 'Discrete Mathematics', 'Logic, sets, functions, relations, combinatorics, graph theory, and proof techniques.', 3, 'SOPHOMORE', []),
            ('CS301', 'Database Systems', 'Database design, SQL, normalization, transactions, and database management systems.', 3, 'JUNIOR', ['CS201']),
            ('CS302', 'Software Engineering', 'Software development lifecycle, design patterns, testing, and project management.', 3, 'JUNIOR', ['CS201']),
            ('CS303', 'Operating Systems', 'Process management, memory management, file systems, and concurrent programming.', 3, 'JUNIOR', ['CS202']),
            ('CS304', 'Computer Networks', 'Network protocols, TCP/IP, routing, network security, and internet applications.', 3, 'JUNIOR', ['CS202']),
            ('CS305', 'Web Development', 'HTML, CSS, JavaScript, frontend frameworks, backend development, and web security.', 3, 'JUNIOR', ['CS201']),
            ('CS401', 'Artificial Intelligence', 'Search algorithms, machine learning, neural networks, and AI applications.', 3, 'SENIOR', ['CS201', 'CS203']),
            ('CS402', 'Machine Learning', 'Supervised and unsupervised learning, deep learning, and model evaluation.', 3, 'SENIOR', ['CS201', 'MATH201']),
            ('CS403', 'Computer Graphics', '3D modeling, rendering, animation, and graphics programming.', 3, 'SENIOR', ['CS201', 'MATH101']),
            ('CS404', 'Cybersecurity', 'Cryptography, network security, secure coding, and security auditing.', 3, 'SENIOR', ['CS304']),
            ('CS405', 'Mobile App Development', 'iOS and Android development, mobile UI/UX, and app deployment.', 3, 'SENIOR', ['CS305']),
        ]
        
        for code, title, desc, credits, level, prereqs in cs_courses:
            course = Course.objects.create(
                course_code=code,
                title=title,
                description=desc,
                credits=credits,
                department='Computer Science',
                level=level,
                is_active=True
            )
            courses[code] = course
            # Add prerequisites
            for prereq_code in prereqs:
                if prereq_code in courses:
                    course.prerequisites.add(courses[prereq_code])
        
        # Mathematics Courses (12 courses)
        math_courses = [
            ('MATH101', 'Calculus I', 'Limits, derivatives, integrals, and applications of calculus.', 4, 'FRESHMAN', []),
            ('MATH102', 'Calculus II', 'Advanced integration techniques, series, and multivariable calculus.', 4, 'FRESHMAN', ['MATH101']),
            ('MATH201', 'Linear Algebra', 'Vectors, matrices, linear transformations, eigenvalues, and eigenvectors.', 3, 'SOPHOMORE', ['MATH101']),
            ('MATH202', 'Differential Equations', 'First and second order differential equations and applications.', 3, 'SOPHOMORE', ['MATH102']),
            ('MATH203', 'Probability and Statistics', 'Probability theory, random variables, distributions, and statistical inference.', 3, 'SOPHOMORE', ['MATH101']),
            ('MATH301', 'Abstract Algebra', 'Groups, rings, fields, and algebraic structures.', 3, 'JUNIOR', ['MATH201']),
            ('MATH302', 'Real Analysis', 'Sequences, series, continuity, differentiation, and integration theory.', 3, 'JUNIOR', ['MATH102']),
            ('MATH303', 'Number Theory', 'Prime numbers, divisibility, congruences, and cryptographic applications.', 3, 'JUNIOR', ['MATH201']),
            ('MATH304', 'Numerical Analysis', 'Numerical methods for solving equations, interpolation, and integration.', 3, 'JUNIOR', ['MATH102', 'CS101']),
            ('MATH401', 'Topology', 'Topological spaces, continuous functions, compactness, and connectedness.', 3, 'SENIOR', ['MATH302']),
            ('MATH402', 'Complex Analysis', 'Complex numbers, analytic functions, complex integration, and residue theory.', 3, 'SENIOR', ['MATH102']),
            ('MATH403', 'Applied Mathematics', 'Mathematical modeling, optimization, and applications in science and engineering.', 3, 'SENIOR', ['MATH202']),
        ]
        
        for code, title, desc, credits, level, prereqs in math_courses:
            course = Course.objects.create(
                course_code=code,
                title=title,
                description=desc,
                credits=credits,
                department='Mathematics',
                level=level,
                is_active=True
            )
            courses[code] = course
            for prereq_code in prereqs:
                if prereq_code in courses:
                    course.prerequisites.add(courses[prereq_code])
        
        # Physics Courses (10 courses)
        physics_courses = [
            ('PHYS101', 'Physics I: Mechanics', 'Kinematics, dynamics, energy, momentum, and rotational motion.', 4, 'FRESHMAN', []),
            ('PHYS101L', 'Physics I Lab', 'Laboratory experiments in mechanics and motion.', 1, 'FRESHMAN', []),
            ('PHYS102', 'Physics II: Electricity and Magnetism', 'Electric fields, magnetic fields, circuits, and electromagnetic waves.', 4, 'FRESHMAN', ['PHYS101']),
            ('PHYS102L', 'Physics II Lab', 'Laboratory experiments in electricity and magnetism.', 1, 'FRESHMAN', ['PHYS101L']),
            ('PHYS201', 'Modern Physics', 'Quantum mechanics, atomic structure, and nuclear physics.', 3, 'SOPHOMORE', ['PHYS102', 'MATH102']),
            ('PHYS301', 'Classical Mechanics', 'Lagrangian and Hamiltonian mechanics, oscillations, and dynamics.', 3, 'JUNIOR', ['PHYS101', 'MATH202']),
            ('PHYS302', 'Electromagnetism', 'Maxwell\'s equations, electromagnetic waves, and radiation.', 3, 'JUNIOR', ['PHYS102', 'MATH202']),
            ('PHYS303', 'Thermodynamics', 'Laws of thermodynamics, heat engines, entropy, and statistical mechanics.', 3, 'JUNIOR', ['PHYS101']),
            ('PHYS401', 'Quantum Mechanics', 'Wave functions, Schrödinger equation, and quantum systems.', 3, 'SENIOR', ['PHYS201', 'MATH202']),
            ('PHYS402', 'Solid State Physics', 'Crystal structures, band theory, and semiconductor physics.', 3, 'SENIOR', ['PHYS201']),
        ]
        
        for code, title, desc, credits, level, prereqs in physics_courses:
            course = Course.objects.create(
                course_code=code,
                title=title,
                description=desc,
                credits=credits,
                department='Physics',
                level=level,
                is_active=True
            )
            courses[code] = course
            for prereq_code in prereqs:
                if prereq_code in courses:
                    course.prerequisites.add(courses[prereq_code])
        
        # Chemistry Courses (8 courses)
        chem_courses = [
            ('CHEM101', 'General Chemistry I', 'Atomic structure, bonding, stoichiometry, and chemical reactions.', 3, 'FRESHMAN', []),
            ('CHEM101L', 'General Chemistry I Lab', 'Laboratory experiments in general chemistry.', 1, 'FRESHMAN', []),
            ('CHEM102', 'General Chemistry II', 'Thermodynamics, kinetics, equilibrium, and electrochemistry.', 3, 'FRESHMAN', ['CHEM101']),
            ('CHEM102L', 'General Chemistry II Lab', 'Laboratory experiments in physical chemistry.', 1, 'FRESHMAN', ['CHEM101L']),
            ('CHEM201', 'Organic Chemistry I', 'Structure, nomenclature, reactions of organic compounds.', 3, 'SOPHOMORE', ['CHEM102']),
            ('CHEM201L', 'Organic Chemistry I Lab', 'Synthesis and analysis of organic compounds.', 1, 'SOPHOMORE', ['CHEM102L']),
            ('CHEM301', 'Physical Chemistry', 'Quantum chemistry, spectroscopy, and molecular structure.', 3, 'JUNIOR', ['CHEM102', 'MATH101', 'PHYS101']),
            ('CHEM302', 'Biochemistry', 'Proteins, enzymes, metabolism, and molecular biology.', 3, 'JUNIOR', ['CHEM201']),
        ]
        
        for code, title, desc, credits, level, prereqs in chem_courses:
            course = Course.objects.create(
                course_code=code,
                title=title,
                description=desc,
                credits=credits,
                department='Chemistry',
                level=level,
                is_active=True
            )
            courses[code] = course
            for prereq_code in prereqs:
                if prereq_code in courses:
                    course.prerequisites.add(courses[prereq_code])
        
        # English Courses (8 courses)
        english_courses = [
            ('ENG101', 'English Composition I', 'Writing skills, grammar, paragraph structure, and essay writing.', 3, 'FRESHMAN', []),
            ('ENG102', 'English Composition II', 'Advanced writing, research papers, and critical analysis.', 3, 'FRESHMAN', ['ENG101']),
            ('ENG201', 'World Literature', 'Survey of world literature from ancient to modern times.', 3, 'SOPHOMORE', ['ENG102']),
            ('ENG202', 'American Literature', 'American literary works from colonial period to present.', 3, 'SOPHOMORE', ['ENG102']),
            ('ENG301', 'Shakespeare', 'Study of Shakespeare\'s plays, sonnets, and literary influence.', 3, 'JUNIOR', ['ENG201']),
            ('ENG302', 'Creative Writing', 'Fiction, poetry, and creative non-fiction writing workshop.', 3, 'JUNIOR', ['ENG102']),
            ('ENG401', 'Literary Theory', 'Critical approaches to literature and cultural studies.', 3, 'SENIOR', ['ENG201']),
            ('ENG402', 'Advanced Writing Workshop', 'Advanced creative writing and professional writing skills.', 3, 'SENIOR', ['ENG302']),
        ]
        
        for code, title, desc, credits, level, prereqs in english_courses:
            course = Course.objects.create(
                course_code=code,
                title=title,
                description=desc,
                credits=credits,
                department='English',
                level=level,
                is_active=True
            )
            courses[code] = course
            for prereq_code in prereqs:
                if prereq_code in courses:
                    course.prerequisites.add(courses[prereq_code])
        
        # History Courses (6 courses)
        history_courses = [
            ('HIST101', 'World History I', 'Ancient civilizations to 1500 CE.', 3, 'FRESHMAN', []),
            ('HIST102', 'World History II', 'Modern world history from 1500 to present.', 3, 'FRESHMAN', []),
            ('HIST201', 'U.S. History I', 'American history from colonial period to Civil War.', 3, 'SOPHOMORE', []),
            ('HIST202', 'U.S. History II', 'American history from Reconstruction to present.', 3, 'SOPHOMORE', []),
            ('HIST301', 'European History', 'European political, social, and cultural history.', 3, 'JUNIOR', ['HIST102']),
            ('HIST401', 'History Seminar', 'Advanced research and analysis in historical topics.', 3, 'SENIOR', ['HIST201']),
        ]
        
        for code, title, desc, credits, level, prereqs in history_courses:
            course = Course.objects.create(
                course_code=code,
                title=title,
                description=desc,
                credits=credits,
                department='History',
                level=level,
                is_active=True
            )
            courses[code] = course
            for prereq_code in prereqs:
                if prereq_code in courses:
                    course.prerequisites.add(courses[prereq_code])
        
        # Create sections with varied schedules
        # Morning classes (8:00 AM - 11:00 AM)
        # Afternoon classes (12:00 PM - 3:00 PM)
        # Evening classes (4:00 PM - 7:00 PM)
        # M/W/F pattern and T/Th pattern
        
        term = 'Fall'
        year = 2024
        
        schedule_patterns = [
            # Morning M/W/F
            ('MWF', time(8, 0), time(8, 50)),
            ('MWF', time(9, 0), time(9, 50)),
            ('MWF', time(10, 0), time(10, 50)),
            ('MWF', time(11, 0), time(11, 50)),
            # Afternoon M/W/F
            ('MWF', time(12, 0), time(12, 50)),
            ('MWF', time(13, 0), time(13, 50)),
            ('MWF', time(14, 0), time(14, 50)),
            ('MWF', time(15, 0), time(15, 50)),
            # Morning T/Th
            ('T/Th', time(8, 0), time(9, 15)),
            ('T/Th', time(9, 30), time(10, 45)),
            ('T/Th', time(11, 0), time(12, 15)),
            # Afternoon T/Th
            ('T/Th', time(12, 30), time(13, 45)),
            ('T/Th', time(14, 0), time(15, 15)),
            ('T/Th', time(15, 30), time(16, 45)),
            # Evening T/Th
            ('T/Th', time(17, 0), time(18, 15)),
            ('T/Th', time(18, 30), time(19, 45)),
            # Labs (longer sessions)
            ('W', time(13, 0), time(15, 50)),
            ('F', time(13, 0), time(15, 50)),
        ]
        
        section_counter = 0
        for course_code, course in courses.items():
            # Create 1-2 sections per course
            num_sections = 2 if 'L' not in course_code else 1  # Labs get 1 section
            
            for i in range(num_sections):
                pattern = schedule_patterns[section_counter % len(schedule_patterns)]
                instructor = instructor_list[section_counter % len(instructor_list)]
                
                meeting_days, start_time, end_time = pattern
                
                CourseSection.objects.create(
                    course=course,
                    section_number=f'{i+1:02d}',
                    term=term,
                    year=year,
                    instructor=instructor,
                    meeting_days=meeting_days,
                    start_time=start_time,
                    end_time=end_time,
                    location=f'Building {(section_counter % 5) + 1} Room {100 + (section_counter % 10)}',
                    campus='Main Campus',
                    max_enrollment=30,
                    current_enrollment=0,
                    crn=f'{10000 + section_counter}',
                    is_available=True
                )
                
                section_counter += 1
        
        self.stdout.write(self.style.SUCCESS(
            f'Successfully created {len(courses)} courses with {section_counter} sections'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'Created sections with varied schedules: morning, afternoon, evening, M/W/F, T/Th, and lab sessions'
        ))
