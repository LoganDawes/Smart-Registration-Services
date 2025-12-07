"""
Serializers for planning models.
"""
from rest_framework import serializers
from .models import StudentPlan, PlannedCourse, ScheduleConflict
from courses.serializers import CourseSectionSerializer
from authentication.models import User


class StudentPlanListSerializer(serializers.ModelSerializer):
    """Serializer for listing student plans (minimal data)."""
    
    student_name = serializers.SerializerMethodField()
    advisor_name = serializers.SerializerMethodField()
    course_count = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentPlan
        fields = [
            'id', 'student', 'student_name', 'advisor', 'advisor_name',
            'term', 'year', 'status', 'name', 'course_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_student_name(self, obj):
        return obj.student.get_full_name() or obj.student.username
    
    def get_advisor_name(self, obj):
        if obj.advisor:
            return obj.advisor.get_full_name() or obj.advisor.username
        return None
    
    def get_course_count(self, obj):
        return obj.planned_courses.count()


class PlannedCourseSerializer(serializers.ModelSerializer):
    """Serializer for planned courses."""
    
    section_details = CourseSectionSerializer(source='section', read_only=True)
    
    class Meta:
        model = PlannedCourse
        fields = [
            'id', 'plan', 'section', 'section_details',
            'priority', 'notes', 'created_at'
        ]
        read_only_fields = ['created_at']


class ScheduleConflictSerializer(serializers.ModelSerializer):
    """Serializer for schedule conflicts."""
    
    course1_details = serializers.SerializerMethodField()
    course2_details = serializers.SerializerMethodField()
    
    class Meta:
        model = ScheduleConflict
        fields = [
            'id', 'plan', 'course1', 'course2',
            'course1_details', 'course2_details',
            'conflict_type', 'description', 'is_resolved',
            'created_at'
        ]
        read_only_fields = ['created_at']
    
    def get_course1_details(self, obj):
        return {
            'id': obj.course1.id,
            'course_code': obj.course1.section.course.course_code,
            'title': obj.course1.section.course.title,
            'section': obj.course1.section.section_number
        }
    
    def get_course2_details(self, obj):
        return {
            'id': obj.course2.id,
            'course_code': obj.course2.section.course.course_code,
            'title': obj.course2.section.course.title,
            'section': obj.course2.section.section_number
        }


class StudentPlanDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed student plan view with all courses and conflicts."""
    
    student_name = serializers.SerializerMethodField()
    advisor_name = serializers.SerializerMethodField()
    planned_courses = PlannedCourseSerializer(many=True, read_only=True)
    conflicts = ScheduleConflictSerializer(many=True, read_only=True)
    total_credits = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentPlan
        fields = [
            'id', 'student', 'student_name', 'advisor', 'advisor_name',
            'term', 'year', 'status', 'name', 'notes', 'advisor_comments',
            'planned_courses', 'conflicts', 'total_credits',
            'submitted_at', 'approved_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'submitted_at', 'approved_at']
    
    def get_student_name(self, obj):
        return obj.student.get_full_name() or obj.student.username
    
    def get_advisor_name(self, obj):
        if obj.advisor:
            return obj.advisor.get_full_name() or obj.advisor.username
        return None
    
    def get_total_credits(self, obj):
        total = sum(
            pc.section.course.credits
            for pc in obj.planned_courses.select_related('section__course').all()
        )
        return total


class CreatePlanSerializer(serializers.ModelSerializer):
    """Serializer for creating a new student plan."""
    
    class Meta:
        model = StudentPlan
        fields = [
            'student', 'advisor', 'term', 'year', 'name', 'notes'
        ]
    
    def validate(self, attrs):
        """Validate that student role is correct."""
        student = attrs.get('student')
        if student and not student.is_student():
            raise serializers.ValidationError("User must have student role")
        
        advisor = attrs.get('advisor')
        if advisor and not advisor.is_advisor():
            raise serializers.ValidationError("Advisor must have advisor role")
        
        return attrs


class AddCourseToPlanSerializer(serializers.Serializer):
    """Serializer for adding a course to a plan."""
    
    section_id = serializers.IntegerField(required=True)
    priority = serializers.IntegerField(default=0, min_value=0)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_section_id(self, value):
        """Validate that section exists and is available."""
        from courses.models import CourseSection
        
        try:
            section = CourseSection.objects.get(id=value)
            if not section.is_available:
                raise serializers.ValidationError("This section is not available for registration")
            return value
        except CourseSection.DoesNotExist:
            raise serializers.ValidationError("Section does not exist")
