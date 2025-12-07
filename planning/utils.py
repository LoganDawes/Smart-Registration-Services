"""
Utility functions for schedule planning and conflict detection.
"""
from datetime import time
from typing import List, Tuple, Dict
from django.db.models import Q
from courses.models import CourseSection
from .models import PlannedCourse, ScheduleConflict


def parse_meeting_days(meeting_days: str) -> List[str]:
    """
    Parse meeting days string into individual days.
    
    Args:
        meeting_days: String like 'MWF', 'TTH', or 'MW'
        
    Returns:
        List of day codes like ['MON', 'WED', 'FRI']
    """
    day_map = {
        'M': 'MON',
        'T': 'TUE',
        'W': 'WED',
        'R': 'THU',  # R is commonly used for Thursday
        'F': 'FRI',
        'S': 'SAT',
        'U': 'SUN'
    }
    
    days = []
    for char in meeting_days.upper():
        if char in day_map:
            days.append(day_map[char])
    
    return days


def check_time_overlap(
    start1: time,
    end1: time,
    start2: time,
    end2: time
) -> bool:
    """
    Check if two time ranges overlap.
    
    Args:
        start1: Start time of first period
        end1: End time of first period
        start2: Start time of second period
        end2: End time of second period
        
    Returns:
        True if times overlap, False otherwise
    """
    # Convert to comparable format (minutes since midnight)
    s1 = start1.hour * 60 + start1.minute
    e1 = end1.hour * 60 + end1.minute
    s2 = start2.hour * 60 + start2.minute
    e2 = end2.hour * 60 + end2.minute
    
    # Check for overlap: start1 < end2 and start2 < end1
    return s1 < e2 and s2 < e1


def check_schedule_conflict(
    section1: CourseSection,
    section2: CourseSection
) -> Tuple[bool, str]:
    """
    Check if two course sections have a schedule conflict.
    
    Args:
        section1: First course section
        section2: Second course section
        
    Returns:
        Tuple of (has_conflict, conflict_description)
    """
    # Parse meeting days for both sections
    days1 = parse_meeting_days(section1.meeting_days)
    days2 = parse_meeting_days(section2.meeting_days)
    
    # Check if they meet on the same day
    common_days = set(days1) & set(days2)
    
    if not common_days:
        return False, ""
    
    # Check if times overlap on common days
    if check_time_overlap(
        section1.start_time,
        section1.end_time,
        section2.start_time,
        section2.end_time
    ):
        day_names = ', '.join(common_days)
        return True, (
            f"Time conflict on {day_names}: "
            f"{section1.course.course_code} meets {section1.start_time.strftime('%I:%M %p')}-"
            f"{section1.end_time.strftime('%I:%M %p')}, "
            f"{section2.course.course_code} meets {section2.start_time.strftime('%I:%M %p')}-"
            f"{section2.end_time.strftime('%I:%M %p')}"
        )
    
    return False, ""


def detect_plan_conflicts(plan) -> List[Dict]:
    """
    Detect all conflicts in a student plan.
    
    Args:
        plan: StudentPlan instance
        
    Returns:
        List of conflict dictionaries with details
    """
    conflicts = []
    planned_courses = plan.planned_courses.select_related(
        'section__course'
    ).all()
    
    # Check for time conflicts between all pairs of courses
    for i, course1 in enumerate(planned_courses):
        for course2 in planned_courses[i + 1:]:
            has_conflict, description = check_schedule_conflict(
                course1.section,
                course2.section
            )
            
            if has_conflict:
                conflicts.append({
                    'type': 'TIME_OVERLAP',
                    'course1': course1,
                    'course2': course2,
                    'description': description
                })
    
    return conflicts


def save_detected_conflicts(plan) -> int:
    """
    Detect conflicts in a plan and save them to the database.
    
    Args:
        plan: StudentPlan instance
        
    Returns:
        Number of conflicts detected and saved
    """
    # Clear existing conflicts for this plan
    ScheduleConflict.objects.filter(plan=plan).delete()
    
    # Detect new conflicts
    conflicts = detect_plan_conflicts(plan)
    
    # Save conflicts to database
    conflict_objects = []
    for conflict in conflicts:
        conflict_obj = ScheduleConflict(
            plan=plan,
            course1=conflict['course1'],
            course2=conflict['course2'],
            conflict_type=conflict['type'],
            description=conflict['description']
        )
        conflict_objects.append(conflict_obj)
    
    if conflict_objects:
        ScheduleConflict.objects.bulk_create(conflict_objects)
    
    return len(conflict_objects)


def check_prerequisites(student, course) -> Tuple[bool, List[str]]:
    """
    Check if a student has completed the prerequisites for a course.
    
    Args:
        student: User instance (student)
        course: Course instance
        
    Returns:
        Tuple of (prerequisites_met, list_of_missing_prerequisites)
    """
    from registration.models import Enrollment
    
    # Get all prerequisites for the course
    prerequisites = course.prerequisites.all()
    
    if not prerequisites.exists():
        return True, []
    
    # Get all courses the student has completed (with passing grade)
    completed_courses = Enrollment.objects.filter(
        student=student,
        status='ENROLLED',
        grade__in=['A', 'B', 'C', 'A+', 'A-', 'B+', 'B-', 'C+', 'C-', 'P', 'S']
    ).values_list('section__course', flat=True)
    
    # Check which prerequisites are missing
    missing_prerequisites = []
    for prereq in prerequisites:
        if prereq.id not in completed_courses:
            missing_prerequisites.append(f"{prereq.course_code} - {prereq.title}")
    
    prerequisites_met = len(missing_prerequisites) == 0
    
    return prerequisites_met, missing_prerequisites


def get_schedule_grid_data(plan) -> Dict:
    """
    Generate schedule grid data for visualization.
    
    Args:
        plan: StudentPlan instance
        
    Returns:
        Dictionary with schedule grid data organized by day and time
    """
    planned_courses = plan.planned_courses.select_related(
        'section__course'
    ).all()
    
    # Days of the week in order
    days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
    
    # Initialize schedule grid
    schedule = {day: [] for day in days}
    
    for planned_course in planned_courses:
        section = planned_course.section
        meeting_days = parse_meeting_days(section.meeting_days)
        
        for day in meeting_days:
            if day in schedule:
                schedule[day].append({
                    'course_code': section.course.course_code,
                    'course_title': section.course.title,
                    'section_number': section.section_number,
                    'start_time': section.start_time,
                    'end_time': section.end_time,
                    'location': section.location,
                    'instructor': section.instructor.get_full_name() if section.instructor else 'TBA',
                    'credits': section.course.credits,
                    'planned_course_id': planned_course.id
                })
    
    # Sort courses by start time for each day
    for day in days:
        schedule[day].sort(key=lambda x: x['start_time'])
    
    return {
        'days': days,
        'schedule': schedule,
        'earliest_time': time(8, 0),  # 8:00 AM
        'latest_time': time(22, 0)     # 10:00 PM
    }
