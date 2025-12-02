from rest_framework import serializers
from .models import Course, CourseSection


class CourseSerializer(serializers.ModelSerializer):
    """Serializer for Course model."""
    
    prerequisites = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    prerequisite_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'course_code', 'title', 'description', 'credits',
            'department', 'level', 'prerequisites', 'prerequisite_details',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_prerequisite_details(self, obj):
        return [
            {'id': prereq.id, 'course_code': prereq.course_code, 'title': prereq.title}
            for prereq in obj.prerequisites.all()
        ]


class CourseSectionSerializer(serializers.ModelSerializer):
    """Serializer for CourseSection model."""
    
    course_details = CourseSerializer(source='course', read_only=True)
    instructor_name = serializers.SerializerMethodField()
    is_full = serializers.SerializerMethodField()
    available_seats = serializers.SerializerMethodField()
    
    class Meta:
        model = CourseSection
        fields = [
            'id', 'course', 'course_details', 'section_number', 'term', 'year',
            'instructor', 'instructor_name', 'max_enrollment', 'current_enrollment',
            'location', 'meeting_days', 'start_time', 'end_time', 'is_available',
            'is_full', 'available_seats', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'current_enrollment']
    
    def get_instructor_name(self, obj):
        return obj.instructor.get_full_name() if obj.instructor else None
    
    def get_is_full(self, obj):
        return obj.is_full()
    
    def get_available_seats(self, obj):
        return obj.max_enrollment - obj.current_enrollment
