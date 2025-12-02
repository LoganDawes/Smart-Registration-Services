from django.contrib import admin
from .models import Course, CourseSection


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_code', 'title', 'department', 'credits', 'level', 'is_active')
    list_filter = ('department', 'level', 'is_active')
    search_fields = ('course_code', 'title', 'description', 'department')
    filter_horizontal = ('prerequisites',)


@admin.register(CourseSection)
class CourseSectionAdmin(admin.ModelAdmin):
    list_display = ('course', 'section_number', 'term', 'year', 'instructor', 'current_enrollment', 'max_enrollment', 'is_available')
    list_filter = ('term', 'year', 'is_available', 'course__department')
    search_fields = ('course__course_code', 'course__title', 'section_number', 'instructor__username')
    raw_id_fields = ('course', 'instructor')

