from django.contrib import admin
from .models import Enrollment, RegistrationRequest, RegistrationLog


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'section', 'status', 'grade', 'enrolled_at')
    list_filter = ('status', 'section__term', 'section__year')
    search_fields = ('student__username', 'section__course__course_code')
    raw_id_fields = ('student', 'section')


@admin.register(RegistrationRequest)
class RegistrationRequestAdmin(admin.ModelAdmin):
    list_display = ('student', 'advisor', 'status', 'submitted_at', 'reviewed_at')
    list_filter = ('status', 'submitted_at', 'reviewed_at')
    search_fields = ('student__username', 'advisor__username')
    raw_id_fields = ('student', 'advisor', 'plan')


@admin.register(RegistrationLog)
class RegistrationLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username',)
    raw_id_fields = ('user', 'enrollment', 'request')

