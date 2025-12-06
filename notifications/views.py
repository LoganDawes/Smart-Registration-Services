from django.shortcuts import render
from django.views.generic import TemplateView
from .models import Notification


class NotificationsView(TemplateView):
    """Notifications page view."""
    template_name = 'notifications/notifications.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get notifications for the current user if authenticated
        if self.request.user.is_authenticated:
            # Get all notifications for the user
            all_notifications = Notification.objects.filter(
                recipient=self.request.user
            ).order_by('-created_at')
            
            # Separate unread and read notifications
            context['unread_notifications'] = all_notifications.filter(is_read=False)
            context['read_notifications'] = all_notifications.filter(is_read=True)
            context['total_notifications'] = all_notifications.count()
            context['unread_count'] = all_notifications.filter(is_read=False).count()
        else:
            context['unread_notifications'] = []
            context['read_notifications'] = []
            context['total_notifications'] = 0
            context['unread_count'] = 0
        
        return context


notifications = NotificationsView.as_view()
