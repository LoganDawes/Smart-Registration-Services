from django.contrib import admin
from .models import StudentPlan, PlannedCourse, ScheduleConflict


class PlannedCourseInline(admin.TabularInline):
    model = PlannedCourse
    extra = 1
    raw_id_fields = ('section',)


@admin.register(StudentPlan)
class StudentPlanAdmin(admin.ModelAdmin):
    list_display = ('student', 'name', 'term', 'year', 'status', 'advisor', 'created_at')
    list_filter = ('status', 'term', 'year')
    search_fields = ('student__username', 'name', 'advisor__username')
    raw_id_fields = ('student', 'advisor')
    inlines = [PlannedCourseInline]


@admin.register(PlannedCourse)
class PlannedCourseAdmin(admin.ModelAdmin):
    list_display = ('plan', 'section', 'priority', 'created_at')
    list_filter = ('priority',)
    search_fields = ('plan__student__username', 'section__course__course_code')
    raw_id_fields = ('plan', 'section')


@admin.register(ScheduleConflict)
class ScheduleConflictAdmin(admin.ModelAdmin):
    list_display = ('plan', 'course1', 'course2', 'conflict_type', 'is_resolved', 'created_at')
    list_filter = ('conflict_type', 'is_resolved')
    search_fields = ('plan__student__username',)
    raw_id_fields = ('plan', 'course1', 'course2')

