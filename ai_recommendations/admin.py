from django.contrib import admin
from .models import DegreeRequirement, CourseRecommendation, RecommendationFeedback


@admin.register(DegreeRequirement)
class DegreeRequirementAdmin(admin.ModelAdmin):
    list_display = ('major', 'requirement_type', 'course', 'credits_required', 'is_active')
    list_filter = ('major', 'requirement_type', 'is_active')
    search_fields = ('major', 'description', 'course__course_code')
    raw_id_fields = ('course',)


@admin.register(CourseRecommendation)
class CourseRecommendationAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'score', 'term', 'year', 'is_accepted', 'created_at')
    list_filter = ('is_accepted', 'term', 'year', 'created_at')
    search_fields = ('student__username', 'course__course_code')
    raw_id_fields = ('student', 'course')


@admin.register(RecommendationFeedback)
class RecommendationFeedbackAdmin(admin.ModelAdmin):
    list_display = ('student', 'recommendation', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('student__username', 'comment')
    raw_id_fields = ('recommendation', 'student')

