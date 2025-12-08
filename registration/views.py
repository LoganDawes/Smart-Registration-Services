from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.db import transaction
from django.http import JsonResponse
import json
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Enrollment, RegistrationRequest, RegistrationLog
from .serializers import (
    EnrollmentSerializer, EnrollmentListSerializer,
    RegistrationRequestSerializer, CreateRegistrationRequestSerializer,
    ApproveRegistrationRequestSerializer, RegistrationLogSerializer,
    EnrollInSectionSerializer, DropEnrollmentSerializer
)
from planning.utils import check_prerequisites, check_schedule_conflict
from planning.models import StudentPlan
from courses.models import CourseSection
from notifications.models import Notification


@method_decorator(login_required, name='dispatch')
class RegistrationView(TemplateView):
    """Registration page view."""
    template_name = 'registration/register.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get student's enrollments
        if self.request.user.is_student():
            enrollments = Enrollment.objects.filter(
                student=self.request.user
            ).select_related('section__course', 'section__instructor').order_by('-enrolled_at')
            
            # Separate by status
            enrolled = enrollments.filter(status=Enrollment.Status.ENROLLED)
            context['enrolled'] = enrolled
            context['waitlisted'] = enrollments.filter(status=Enrollment.Status.WAITLISTED)
            context['dropped'] = enrollments.filter(status=Enrollment.Status.DROPPED)
            
            # Calculate total credits
            context['total_credits'] = sum(e.section.course.credits for e in enrolled)
            
            # Get added courses items from session
            added_courses = self.request.session.get('added_courses', [])
            if added_courses:
                added_courses_sections = CourseSection.objects.filter(
                    id__in=added_courses,
                    is_available=True
                ).select_related('course', 'instructor')
                context['added_courses_items'] = added_courses_sections
            else:
                context['added_courses_items'] = []
        
        return context


registration_page = RegistrationView.as_view()


class EnrollmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing enrollments.
    
    Endpoints:
    - list: Get enrollments for current user (students) or all (advisors/registrar)
    - retrieve: Get detailed enrollment information
    - my_enrollments: Get current enrollments for logged-in student
    - by_section: Get enrollments for a specific section
    """
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return enrollments based on user role."""
        user = self.request.user
        
        if user.is_student():
            # Students see only their own enrollments
            return Enrollment.objects.filter(student=user)
        elif user.is_advisor():
            # Advisors see enrollments of their advisees
            # For now, show all - can be filtered based on advisor assignments
            return Enrollment.objects.all()
        elif user.is_registrar():
            # Registrar sees all enrollments
            return Enrollment.objects.all()
        
        return Enrollment.objects.none()
    
    def get_serializer_class(self):
        """Use lightweight serializer for list view."""
        if self.action == 'list' or self.action == 'my_enrollments':
            return EnrollmentListSerializer
        return EnrollmentSerializer
    
    @action(detail=False, methods=['get'])
    def my_enrollments(self, request):
        """Get current enrollments for logged-in student."""
        if not request.user.is_student():
            return Response(
                {'error': 'Only students can view their enrollments'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        enrollments = Enrollment.objects.filter(
            student=request.user
        ).select_related('section__course')
        
        # Group by status
        enrolled = enrollments.filter(status=Enrollment.Status.ENROLLED)
        waitlisted = enrollments.filter(status=Enrollment.Status.WAITLISTED)
        
        serializer = self.get_serializer(enrolled, many=True)
        waitlist_serializer = self.get_serializer(waitlisted, many=True)
        
        return Response({
            'enrolled': serializer.data,
            'waitlisted': waitlist_serializer.data,
            'total_credits': sum(e.section.course.credits for e in enrolled)
        })
    
    @action(detail=False, methods=['get'])
    def by_section(self, request):
        """Get enrollments for a specific section."""
        section_id = request.query_params.get('section_id')
        
        if not section_id:
            return Response(
                {'error': 'section_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        enrollments = Enrollment.objects.filter(
            section_id=section_id
        ).select_related('student', 'section__course')
        
        serializer = self.get_serializer(enrollments, many=True)
        return Response(serializer.data)


class RegistrationRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing registration requests.
    
    Endpoints:
    - list: Get registration requests
    - retrieve: Get detailed request information
    - create: Create a new registration request
    - approve_reject: Approve or reject a request (advisors only)
    - my_requests: Get requests for logged-in student
    - pending_for_advisor: Get pending requests for logged-in advisor
    """
    serializer_class = RegistrationRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return requests based on user role."""
        user = self.request.user
        
        if user.is_student():
            # Students see only their own requests
            return RegistrationRequest.objects.filter(student=user)
        elif user.is_advisor():
            # Advisors see requests assigned to them
            return RegistrationRequest.objects.filter(advisor=user)
        elif user.is_registrar():
            # Registrar sees all requests
            return RegistrationRequest.objects.all()
        
        return RegistrationRequest.objects.none()
    
    def get_serializer_class(self):
        """Use different serializers for different actions."""
        if self.action == 'create':
            return CreateRegistrationRequestSerializer
        elif self.action == 'approve_reject':
            return ApproveRegistrationRequestSerializer
        return RegistrationRequestSerializer
    
    def perform_create(self, serializer):
        """Set student to current user if not provided."""
        if not serializer.validated_data.get('student'):
            serializer.save(student=self.request.user)
        else:
            serializer.save()
    
    @action(detail=True, methods=['post'])
    def approve_reject(self, request, pk=None):
        """Approve or reject a registration request (advisors only)."""
        if not request.user.is_advisor():
            return Response(
                {'error': 'Only advisors can approve/reject requests'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        registration_request = self.get_object()
        
        if registration_request.status != RegistrationRequest.Status.PENDING:
            return Response(
                {'error': 'Only pending requests can be approved/rejected'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ApproveRegistrationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        action_type = serializer.validated_data['action']
        advisor_comments = serializer.validated_data.get('advisor_comments', '')
        
        with transaction.atomic():
            if action_type == 'approve':
                registration_request.status = RegistrationRequest.Status.APPROVED
            else:
                registration_request.status = RegistrationRequest.Status.REJECTED
            
            registration_request.advisor_comments = advisor_comments
            registration_request.reviewed_at = timezone.now()
            registration_request.advisor = request.user
            registration_request.save()
            
            # Log the action
            RegistrationLog.objects.create(
                user=request.user,
                request=registration_request,
                action=RegistrationLog.Action.APPROVE if action_type == 'approve' else RegistrationLog.Action.REJECT,
                details={
                    'advisor_comments': advisor_comments,
                    'student': registration_request.student.username
                }
            )
        
        return Response(
            RegistrationRequestSerializer(registration_request).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def my_requests(self, request):
        """Get requests for logged-in student."""
        if not request.user.is_student():
            return Response(
                {'error': 'Only students can view their requests'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        requests = RegistrationRequest.objects.filter(
            student=request.user
        ).order_by('-submitted_at')
        
        serializer = self.get_serializer(requests, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending_for_advisor(self, request):
        """Get pending requests for logged-in advisor."""
        if not request.user.is_advisor():
            return Response(
                {'error': 'Only advisors can view pending requests'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        requests = RegistrationRequest.objects.filter(
            advisor=request.user,
            status=RegistrationRequest.Status.PENDING
        ).order_by('submitted_at')
        
        serializer = self.get_serializer(requests, many=True)
        return Response(serializer.data)


class RegistrationActionViewSet(viewsets.ViewSet):
    """
    ViewSet for registration actions (enroll, drop).
    
    Endpoints:
    - enroll: Enroll in a course section
    - drop: Drop an enrollment
    - check_eligibility: Check if student is eligible to enroll in a section
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def enroll(self, request):
        """Enroll student in a course section."""
        if not request.user.is_student():
            return Response(
                {'error': 'Only students can enroll in courses'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = EnrollInSectionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        section_id = serializer.validated_data['section_id']
        section = get_object_or_404(CourseSection, id=section_id)
        
        # Check if already enrolled
        if Enrollment.objects.filter(
            student=request.user,
            section=section,
            status=Enrollment.Status.ENROLLED
        ).exists():
            return Response(
                {'error': 'You are already enrolled in this section'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # REMOVED: Prerequisite validation per institutional policy change
        # Students may now register for any course regardless of prerequisite completion
        # This allows flexible enrollment paths and student autonomy in course selection
        # # Check prerequisites
        # prereqs_met, missing = check_prerequisites(request.user, section.course)
        # if not prereqs_met:
        #     return Response(
        #         {
        #             'error': 'Prerequisites not met',
        #             'missing_prerequisites': missing
        #         },
        #         status=status.HTTP_400_BAD_REQUEST
        #     )
        
        # Check for schedule conflicts
        current_enrollments = Enrollment.objects.filter(
            student=request.user,
            status=Enrollment.Status.ENROLLED,
            section__term=section.term,
            section__year=section.year
        ).select_related('section')
        
        for enrollment in current_enrollments:
            has_conflict, description = check_schedule_conflict(
                enrollment.section,
                section
            )
            if has_conflict:
                return Response(
                    {'error': 'Schedule conflict', 'details': description},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Enroll or waitlist
        with transaction.atomic():
            if section.is_full():
                enrollment_status = Enrollment.Status.WAITLISTED
                action = RegistrationLog.Action.WAITLIST
            else:
                enrollment_status = Enrollment.Status.ENROLLED
                action = RegistrationLog.Action.REGISTER
                # Update enrollment count
                section.current_enrollment += 1
                section.save()
            
            enrollment = Enrollment.objects.create(
                student=request.user,
                section=section,
                status=enrollment_status
            )
            
            # Log the action
            RegistrationLog.objects.create(
                user=request.user,
                enrollment=enrollment,
                action=action,
                details={
                    'course_code': section.course.course_code,
                    'section': section.section_number,
                    'term': section.term,
                    'year': section.year
                }
            )
        
        return Response(
            EnrollmentSerializer(enrollment).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['post'])
    def drop(self, request):
        """Drop an enrollment."""
        if not request.user.is_student() and not (request.user.is_staff and request.user.is_superuser):
            return Response(
                {'error': 'Only students or superuser staff can drop enrollments'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = DropEnrollmentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        enrollment_id = serializer.validated_data['enrollment_id']
        
        # Allow admin to drop any enrollment, students only their own
        if request.user.is_student():
            enrollment = get_object_or_404(
                Enrollment,
                id=enrollment_id,
                student=request.user
            )
        else:
            enrollment = get_object_or_404(Enrollment, id=enrollment_id)
        
        # Check if already dropped
        if enrollment.status == Enrollment.Status.DROPPED:
            return Response(
                {'error': 'This enrollment has already been dropped'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            # Update enrollment status
            old_status = enrollment.status
            enrollment.status = Enrollment.Status.DROPPED
            enrollment.dropped_at = timezone.now()
            enrollment.save()
            
            # Update section enrollment count only if was enrolled (not waitlisted)
            if old_status == Enrollment.Status.ENROLLED:
                if enrollment.section.current_enrollment > 0:
                    enrollment.section.current_enrollment -= 1
                    enrollment.section.save()
            
            # Log the action
            RegistrationLog.objects.create(
                user=request.user,
                enrollment=enrollment,
                action=RegistrationLog.Action.DROP,
                details={
                    'course_code': enrollment.section.course.course_code,
                    'section': enrollment.section.section_number,
                    'term': enrollment.section.term,
                    'year': enrollment.section.year,
                    'previous_status': old_status
                }
            )
        
        return Response(
            {'message': 'Enrollment dropped successfully'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['post'])
    def check_eligibility(self, request):
        """Check if student is eligible to enroll in a section."""
        if not request.user.is_student():
            return Response(
                {'error': 'Only students can check eligibility'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        section_id = request.data.get('section_id')
        if not section_id:
            return Response(
                {'error': 'section_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        section = get_object_or_404(CourseSection, id=section_id)
        
        issues = []
        
        # Check if section is available
        if not section.is_available:
            issues.append('Section is not available for registration')
        
        # Check if already enrolled
        if Enrollment.objects.filter(
            student=request.user,
            section=section,
            status=Enrollment.Status.ENROLLED
        ).exists():
            issues.append('Already enrolled in this section')
        
        # REMOVED: Prerequisite validation per institutional policy change
        # Students may now register for any course regardless of prerequisite completion
        # # Check prerequisites
        # prereqs_met, missing = check_prerequisites(request.user, section.course)
        # if not prereqs_met:
        #     issues.append(f'Missing prerequisites: {", ".join(missing)}')
        
        # Check for conflicts
        current_enrollments = Enrollment.objects.filter(
            student=request.user,
            status=Enrollment.Status.ENROLLED,
            section__term=section.term,
            section__year=section.year
        ).select_related('section')
        
        for enrollment in current_enrollments:
            has_conflict, description = check_schedule_conflict(
                enrollment.section,
                section
            )
            if has_conflict:
                issues.append(description)
        
        # Check capacity
        seats_available = section.available_seats()
        
        return Response({
            'eligible': len(issues) == 0,
            'issues': issues,
            'seats_available': seats_available,
            'will_be_waitlisted': section.is_full()
        })


class RegistrationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing registration logs.
    
    Read-only access for auditing purposes.
    """
    serializer_class = RegistrationLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return logs based on user role."""
        user = self.request.user
        
        if user.is_student():
            # Students see only their own logs
            return RegistrationLog.objects.filter(user=user)
        elif user.is_advisor() or user.is_registrar():
            # Advisors and registrar see all logs
            return RegistrationLog.objects.all()
        
        return RegistrationLog.objects.none()


@login_required
def load_plan_form(request):
    """View to show load plan modal."""
    # Get user's plans with total credits
    plans = StudentPlan.objects.filter(
        student=request.user
    ).prefetch_related('planned_courses__section__course').order_by('-created_at')
    
    # Add total credits to each plan
    for plan in plans:
        plan.total_credits = sum(
            pc.section.course.credits 
            for pc in plan.planned_courses.all()
        )
    
    return render(request, 'registration/load_plan_modal.html', {
        'plans': plans
    })


@login_required
def load_plan_to_added_courses(request, plan_id):
    """Load all courses from a plan into the added courses list."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    plan = get_object_or_404(StudentPlan, id=plan_id, student=request.user)
    
    # Get all planned courses
    planned_courses = plan.planned_courses.select_related('section', 'section__course').all()
    
    # Get or create added courses list in session
    added_courses = request.session.get('added_courses', [])
    
    # Add sections to added courses (avoid duplicates)
    added = 0
    for pc in planned_courses:
        section_id = pc.section.id
        if section_id not in added_courses:
            added_courses.append(section_id)
            added += 1
    
    request.session['added_courses'] = added_courses
    
    return JsonResponse({
        'success': True,
        'count': added,
        'total_in_added_courses': len(added_courses)
    })


@login_required
def add_to_added_courses(request):
    """Add a course section to the added courses list."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    data = json.loads(request.body)
    section_id = data.get('section_id')
    
    if not section_id:
        return JsonResponse({'error': 'section_id is required'}, status=400)
    
    # Verify section exists
    section = get_object_or_404(CourseSection, id=section_id, is_available=True)
    
    # Get or create added courses list in session
    added_courses = request.session.get('added_courses', [])
    
    if section_id not in added_courses:
        added_courses.append(section_id)
        request.session['added_courses'] = added_courses
        return JsonResponse({
            'success': True, 
            'message': 'Course added to Added Courses',
            'total_count': len(added_courses)
        })
    else:
        return JsonResponse({'success': False, 'error': 'Course already in Added Courses'}, status=400)


@login_required
def remove_from_added_courses(request):
    """Remove a course section from the added courses list."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    data = json.loads(request.body)
    section_id = data.get('section_id')
    
    if not section_id:
        return JsonResponse({'error': 'section_id is required'}, status=400)
    
    added_courses = request.session.get('added_courses', [])
    
    if section_id in added_courses:
        added_courses.remove(section_id)
        request.session['added_courses'] = added_courses
        return JsonResponse({
            'success': True, 
            'message': 'Course removed from Added Courses',
            'total_count': len(added_courses)
        })
    else:
        return JsonResponse({'success': False, 'error': 'Course not in Added Courses'}, status=400)


@login_required
def confirm_all_registration(request):
    """Register for all courses in the cart."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    data = json.loads(request.body)
    section_ids = data.get('section_ids', [])
    
    if not section_ids:
        return JsonResponse({'error': 'No courses in cart'}, status=400)
    
    registered = 0
    failed = []
    
    for section_id in section_ids:
        try:
            section = CourseSection.objects.get(id=section_id, is_available=True)
            
            # Check if already enrolled
            if Enrollment.objects.filter(
                student=request.user,
                section=section,
                status=Enrollment.Status.ENROLLED
            ).exists():
                failed.append({
                    'section_id': section_id,
                    'error': f'Already enrolled in {section.course.course_code}'
                })
                continue
            
            # REMOVED: Prerequisite validation per institutional policy change
            # Students may now register for any course regardless of prerequisite completion
            # # Check prerequisites
            # prereqs_met, missing = check_prerequisites(request.user, section.course)
            # if not prereqs_met:
            #     failed.append({
            #         'section_id': section_id,
            #         'error': f'{section.course.course_code}: Missing prerequisites'
            #     })
            #     continue
            
            # Check for conflicts
            current_enrollments = Enrollment.objects.filter(
                student=request.user,
                status=Enrollment.Status.ENROLLED,
                section__term=section.term,
                section__year=section.year
            ).select_related('section')
            
            has_conflict = False
            for enrollment in current_enrollments:
                conflict, description = check_schedule_conflict(
                    enrollment.section,
                    section
                )
                if conflict:
                    failed.append({
                        'section_id': section_id,
                        'error': f'{section.course.course_code}: {description}'
                    })
                    has_conflict = True
                    break
            
            if has_conflict:
                continue
            
            # Enroll or waitlist
            with transaction.atomic():
                if section.is_full():
                    enrollment_status = Enrollment.Status.WAITLISTED
                else:
                    enrollment_status = Enrollment.Status.ENROLLED
                    section.current_enrollment += 1
                    section.save()
                
                Enrollment.objects.create(
                    student=request.user,
                    section=section,
                    status=enrollment_status
                )
                
                registered += 1
        
        except CourseSection.DoesNotExist:
            failed.append({
                'section_id': section_id,
                'error': 'Section not found or unavailable'
            })
        except Exception as e:
            failed.append({
                'section_id': section_id,
                'error': str(e)
            })
    
    # Clear added courses on success
    if registered > 0:
        request.session['added_courses'] = []
        
        # Create enrollment confirmed notification
        Notification.objects.create(
            recipient=request.user,
            notification_type=Notification.Type.ENROLLMENT_CONFIRMED,
            title='Enrollment Confirmed',
            message=f'You have successfully registered for {registered} course(s).',
            link='/registration/register/',
            is_sent=True,
            sent_at=timezone.now()
        )
    
    return JsonResponse({
        'success': True,
        'registered': registered,
        'failed': failed
    })
