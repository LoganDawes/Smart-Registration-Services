from django.contrib import admin
from .models import AdvisorAssignment, ChatMessage, PlanComment


@admin.register(AdvisorAssignment)
class AdvisorAssignmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'advisor', 'is_active', 'assigned_at')
    list_filter = ('is_active', 'assigned_at')
    search_fields = ('student__username', 'advisor__username')
    raw_id_fields = ('student', 'advisor')


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'is_read', 'sent_at')
    list_filter = ('is_read', 'sent_at')
    search_fields = ('sender__username', 'recipient__username', 'message')
    raw_id_fields = ('sender', 'recipient', 'plan')


@admin.register(PlanComment)
class PlanCommentAdmin(admin.ModelAdmin):
    list_display = ('plan', 'advisor', 'requires_change', 'is_resolved', 'created_at')
    list_filter = ('requires_change', 'is_resolved', 'created_at')
    search_fields = ('plan__student__username', 'advisor__username', 'comment')
    raw_id_fields = ('plan', 'advisor')

