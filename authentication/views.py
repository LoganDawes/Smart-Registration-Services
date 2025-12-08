from django.shortcuts import render
from django.views.generic import TemplateView
from notifications.models import Notification
from planning.models import StudentPlan
from registration.models import Enrollment


class HomeView(TemplateView):
    """Home page view."""
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.user.is_authenticated:
            # Get unread notifications count
            unread_count = Notification.objects.filter(
                recipient=self.request.user,
                is_read=False
            ).count()
            context['unread_notifications'] = unread_count
            
            # Get active plans count
            active_plans = StudentPlan.objects.filter(
                student=self.request.user
            ).count()
            context['active_plans'] = active_plans
            
            # Get enrolled courses count
            enrolled_count = Enrollment.objects.filter(
                student=self.request.user,
                status=Enrollment.Status.ENROLLED
            ).count()
            context['enrolled_courses'] = enrolled_count
        
        return context


home = HomeView.as_view()

