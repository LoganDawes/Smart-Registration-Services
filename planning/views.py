from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import StudentPlan, PlannedCourse, ScheduleConflict
from .serializers import (
    StudentPlanListSerializer, StudentPlanDetailSerializer,
    CreatePlanSerializer, PlannedCourseSerializer,
    AddCourseToPlanSerializer, ScheduleConflictSerializer
)
from .utils import save_detected_conflicts, check_prerequisites, get_schedule_grid_data
from courses.models import CourseSection


@method_decorator(login_required, name='dispatch')
class SchedulePlanningView(TemplateView):
    """Schedule page view - displays registered courses in calendar format."""
    template_name = 'planning/schedule.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get student's enrolled courses only (not plans)
        if self.request.user.is_student():
            from registration.models import Enrollment
            from .utils import parse_meeting_days
            
            # Get all enrolled courses for the student
            enrollments = Enrollment.objects.filter(
                student=self.request.user,
                status=Enrollment.Status.ENROLLED
            ).select_related('section__course', 'section__instructor').order_by('section__start_time')
            
            context['enrollments'] = enrollments
            
            # Calculate total credits
            total_credits = sum(e.section.course.credits for e in enrollments)
            context['total_credits'] = total_credits
            
            # Generate schedule grid data for calendar view
            days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
            schedule = {day: [] for day in days}
            
            for enrollment in enrollments:
                section = enrollment.section
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
                            'enrollment_id': enrollment.id
                        })
            
            # Sort courses by start time for each day
            for day in days:
                schedule[day].sort(key=lambda x: x['start_time'])
            
            context['schedule_data'] = {
                'days': days,
                'schedule': schedule
            }
            
            # Create time slots for schedule grid (7 AM to 10 PM)
            time_slots = []
            for hour in range(7, 22):
                # Proper 12-hour format conversion
                if hour < 12:
                    display_hour = hour
                    period = 'AM'
                elif hour == 12:
                    display_hour = 12
                    period = 'PM'
                else:
                    display_hour = hour - 12
                    period = 'PM'
                
                time_slots.append({
                    'hour': hour,
                    'display': f"{display_hour}:00",
                    'period': period
                })
            context['time_slots'] = time_slots
        
        return context


schedule_planning = SchedulePlanningView.as_view()


class StudentPlanViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing student course plans.
    
    Endpoints:
    - list: Get all plans for current user (student) or assigned students (advisor)
    - retrieve: Get detailed plan with courses and conflicts
    - create: Create a new plan
    - update/partial_update: Update plan details
    - destroy: Delete a plan
    - add_course: Add a course to the plan
    - remove_course: Remove a course from the plan
    - detect_conflicts: Run conflict detection
    - submit: Submit plan for advisor approval
    - approve: Approve a plan (advisors only)
    - reject: Reject a plan (advisors only)
    """
    serializer_class = StudentPlanListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return plans based on user role."""
        user = self.request.user
        
        if user.is_student():
            # Students see only their own plans
            return StudentPlan.objects.filter(student=user)
        elif user.is_advisor():
            # Advisors see plans they're assigned to
            return StudentPlan.objects.filter(advisor=user)
        elif user.is_registrar():
            # Registrar sees all plans
            return StudentPlan.objects.all()
        
        return StudentPlan.objects.none()
    
    def get_serializer_class(self):
        """Use different serializers for different actions."""
        if self.action == 'retrieve':
            return StudentPlanDetailSerializer
        elif self.action == 'create':
            return CreatePlanSerializer
        return StudentPlanListSerializer
    
    def perform_create(self, serializer):
        """Set student to current user if not provided."""
        if not serializer.validated_data.get('student'):
            serializer.save(student=self.request.user)
        else:
            serializer.save()
    
    @action(detail=True, methods=['post'])
    def add_course(self, request, pk=None):
        """Add a course section to the plan."""
        plan = self.get_object()
        
        # Check permissions
        if request.user != plan.student and not request.user.is_advisor():
            return Response(
                {'error': 'You do not have permission to modify this plan'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = AddCourseToPlanSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        section_id = serializer.validated_data['section_id']
        section = get_object_or_404(CourseSection, id=section_id)
        
        # Check if already in plan
        if PlannedCourse.objects.filter(plan=plan, section=section).exists():
            return Response(
                {'error': 'This course is already in the plan'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check prerequisites
        prereqs_met, missing = check_prerequisites(plan.student, section.course)
        if not prereqs_met:
            return Response(
                {
                    'error': 'Prerequisites not met',
                    'missing_prerequisites': missing
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Add course to plan
        planned_course = PlannedCourse.objects.create(
            plan=plan,
            section=section,
            priority=serializer.validated_data.get('priority', 0),
            notes=serializer.validated_data.get('notes', '')
        )
        
        # Detect conflicts
        save_detected_conflicts(plan)
        
        return Response(
            PlannedCourseSerializer(planned_course).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def remove_course(self, request, pk=None):
        """Remove a course from the plan."""
        plan = self.get_object()
        
        # Check permissions
        if request.user != plan.student and not request.user.is_advisor():
            return Response(
                {'error': 'You do not have permission to modify this plan'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        planned_course_id = request.data.get('planned_course_id')
        if not planned_course_id:
            return Response(
                {'error': 'planned_course_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        planned_course = get_object_or_404(
            PlannedCourse,
            id=planned_course_id,
            plan=plan
        )
        
        planned_course.delete()
        
        # Redetect conflicts
        save_detected_conflicts(plan)
        
        return Response(
            {'message': 'Course removed from plan'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def detect_conflicts(self, request, pk=None):
        """Run conflict detection on the plan."""
        plan = self.get_object()
        
        conflicts_count = save_detected_conflicts(plan)
        
        return Response({
            'message': f'Detected {conflicts_count} conflicts',
            'conflicts_count': conflicts_count,
            'conflicts': ScheduleConflictSerializer(
                plan.conflicts.all(),
                many=True
            ).data
        })
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit plan for advisor approval."""
        plan = self.get_object()
        
        # Check permissions
        if request.user != plan.student:
            return Response(
                {'error': 'Only the student can submit their plan'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if plan.status != StudentPlan.Status.DRAFT:
            return Response(
                {'error': 'Only draft plans can be submitted'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check for conflicts
        if plan.conflicts.filter(is_resolved=False).exists():
            return Response(
                {'error': 'Please resolve all conflicts before submitting'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        plan.status = StudentPlan.Status.SUBMITTED
        plan.submitted_at = timezone.now()
        plan.save()
        
        return Response(
            StudentPlanDetailSerializer(plan).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a plan (advisors only)."""
        plan = self.get_object()
        
        # Check permissions
        if not request.user.is_advisor():
            return Response(
                {'error': 'Only advisors can approve plans'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if plan.status != StudentPlan.Status.SUBMITTED:
            return Response(
                {'error': 'Only submitted plans can be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        plan.status = StudentPlan.Status.APPROVED
        plan.approved_at = timezone.now()
        plan.advisor_comments = request.data.get('advisor_comments', '')
        plan.save()
        
        return Response(
            StudentPlanDetailSerializer(plan).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a plan (advisors only)."""
        plan = self.get_object()
        
        # Check permissions
        if not request.user.is_advisor():
            return Response(
                {'error': 'Only advisors can reject plans'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if plan.status != StudentPlan.Status.SUBMITTED:
            return Response(
                {'error': 'Only submitted plans can be rejected'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        advisor_comments = request.data.get('advisor_comments', '')
        if not advisor_comments:
            return Response(
                {'error': 'Advisor comments are required when rejecting'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        plan.status = StudentPlan.Status.REJECTED
        plan.advisor_comments = advisor_comments
        plan.save()
        
        return Response(
            StudentPlanDetailSerializer(plan).data,
            status=status.HTTP_200_OK
        )


@login_required
def select_plan_form(request):
    """View to show plan selector modal."""
    section_id = request.GET.get('section_id')
    
    # Get user's plans (only DRAFT plans can be edited)
    plans = StudentPlan.objects.filter(
        student=request.user,
        status=StudentPlan.Status.DRAFT
    ).prefetch_related('planned_courses').order_by('-created_at')
    
    return render(request, 'planning/select_plan_modal.html', {
        'plans': plans,
        'section_id': section_id
    })
