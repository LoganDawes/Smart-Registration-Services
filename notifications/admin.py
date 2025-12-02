from django.contrib import admin
from .models import Notification, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'notification_type', 'title', 'is_read', 'is_sent', 'send_email', 'created_at')
    list_filter = ('notification_type', 'is_read', 'is_sent', 'send_email', 'created_at')
    search_fields = ('recipient__username', 'title', 'message')
    raw_id_fields = ('recipient',)


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_notifications', 'push_notifications', 'updated_at')
    list_filter = ('email_notifications', 'push_notifications')
    search_fields = ('user__username',)
    raw_id_fields = ('user',)

