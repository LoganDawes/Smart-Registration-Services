"""
Serializers for registration models.
"""
from rest_framework import serializers
from django.utils import timezone
from .models import Enrollment, RegistrationRequest, RegistrationLog
from courses.serializers import CourseSectionSerializer
from planning.serializers import StudentPlanListSerializer


class EnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for enrollments."""
    
    section_details = CourseSectionSerializer(source='section', read_only=True)
    student_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'student', 'student_name', 'section', 'section_details',
            'status', 'grade', 'enrolled_at', 'dropped_at', 'updated_at'
        ]
        read_only_fields = ['enrolled_at', 'updated_at']
    
    def get_student_name(self, obj):
        return obj.student.get_full_name() or obj.student.username


class EnrollmentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing enrollments."""
    
    course_code = serializers.CharField(source='section.course.course_code', read_only=True)
    course_title = serializers.CharField(source='section.course.title', read_only=True)
    section_number = serializers.CharField(source='section.section_number', read_only=True)
    term = serializers.CharField(source='section.term', read_only=True)
    year = serializers.IntegerField(source='section.year', read_only=True)
    credits = serializers.IntegerField(source='section.course.credits', read_only=True)
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'status', 'grade', 'course_code', 'course_title',
            'section_number', 'term', 'year', 'credits', 'enrolled_at'
        ]


class RegistrationRequestSerializer(serializers.ModelSerializer):
    """Serializer for registration requests."""
    
    student_name = serializers.SerializerMethodField()
    advisor_name = serializers.SerializerMethodField()
    plan_details = StudentPlanListSerializer(source='plan', read_only=True)
    
    class Meta:
        model = RegistrationRequest
        fields = [
            'id', 'student', 'student_name', 'advisor', 'advisor_name',
            'plan', 'plan_details', 'status', 'notes', 'advisor_comments',
            'submitted_at', 'reviewed_at', 'completed_at'
        ]
        read_only_fields = ['submitted_at', 'reviewed_at', 'completed_at']
    
    def get_student_name(self, obj):
        return obj.student.get_full_name() or obj.student.username
    
    def get_advisor_name(self, obj):
        if obj.advisor:
            return obj.advisor.get_full_name() or obj.advisor.username
        return None


class CreateRegistrationRequestSerializer(serializers.ModelSerializer):
    """Serializer for creating registration requests."""
    
    class Meta:
        model = RegistrationRequest
        fields = ['student', 'advisor', 'plan', 'notes']
    
    def validate(self, attrs):
        """Validate request data."""
        student = attrs.get('student')
        if student and not student.is_student():
            raise serializers.ValidationError("User must have student role")
        
        advisor = attrs.get('advisor')
        if advisor and not advisor.is_advisor():
            raise serializers.ValidationError("Advisor must have advisor role")
        
        plan = attrs.get('plan')
        if plan and plan.student != student:
            raise serializers.ValidationError("Plan must belong to the student")
        
        return attrs


class ApproveRegistrationRequestSerializer(serializers.Serializer):
    """Serializer for approving/rejecting registration requests."""
    
    action = serializers.ChoiceField(choices=['approve', 'reject'], required=True)
    advisor_comments = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, attrs):
        """Ensure advisor comments provided for rejection."""
        if attrs['action'] == 'reject' and not attrs.get('advisor_comments'):
            raise serializers.ValidationError(
                "Advisor comments are required when rejecting a request"
            )
        return attrs


class RegistrationLogSerializer(serializers.ModelSerializer):
    """Serializer for registration logs."""
    
    user_name = serializers.SerializerMethodField()
    enrollment_details = serializers.SerializerMethodField()
    
    class Meta:
        model = RegistrationLog
        fields = [
            'id', 'user', 'user_name', 'enrollment', 'enrollment_details',
            'request', 'action', 'details', 'timestamp'
        ]
        read_only_fields = ['timestamp']
    
    def get_user_name(self, obj):
        if obj.user:
            return obj.user.get_full_name() or obj.user.username
        return None
    
    def get_enrollment_details(self, obj):
        if obj.enrollment:
            return {
                'course_code': obj.enrollment.section.course.course_code,
                'section': obj.enrollment.section.section_number,
                'term': obj.enrollment.section.term,
                'year': obj.enrollment.section.year
            }
        return None


class EnrollInSectionSerializer(serializers.Serializer):
    """Serializer for enrolling in a section."""
    
    section_id = serializers.IntegerField(required=True)
    
    def validate_section_id(self, value):
        """Validate that section exists and has capacity."""
        from courses.models import CourseSection
        
        try:
            section = CourseSection.objects.get(id=value)
            if not section.is_available:
                raise serializers.ValidationError("This section is not available")
            if section.is_full():
                raise serializers.ValidationError("This section is full")
            return value
        except CourseSection.DoesNotExist:
            raise serializers.ValidationError("Section does not exist")


class DropEnrollmentSerializer(serializers.Serializer):
    """Serializer for dropping an enrollment."""
    
    enrollment_id = serializers.IntegerField(required=True)
    
    def validate_enrollment_id(self, value):
        """Validate that enrollment exists."""
        try:
            enrollment = Enrollment.objects.get(id=value)
            if enrollment.status == Enrollment.Status.DROPPED:
                raise serializers.ValidationError("Enrollment already dropped")
            return value
        except Enrollment.DoesNotExist:
            raise serializers.ValidationError("Enrollment does not exist")
