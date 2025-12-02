from django.contrib import admin
from .models import SystemLog, APIMetrics


@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ('level', 'module', 'message_preview', 'user', 'timestamp')
    list_filter = ('level', 'module', 'timestamp')
    search_fields = ('message', 'module', 'user__username')
    raw_id_fields = ('user',)
    
    def message_preview(self, obj):
        return obj.message[:100]
    message_preview.short_description = 'Message'


@admin.register(APIMetrics)
class APIMetricsAdmin(admin.ModelAdmin):
    list_display = ('method', 'endpoint', 'status_code', 'response_time', 'user', 'timestamp')
    list_filter = ('method', 'status_code', 'timestamp')
    search_fields = ('endpoint', 'user__username')
    raw_id_fields = ('user',)

