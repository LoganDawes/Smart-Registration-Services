from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.generic import TemplateView
from .models import CourseRecommendation

# from .models import CourseRecommendation
# Use these if you need login/permission checks:
# from django.contrib.auth.decorators import login_required


class AIRecommendationsView(TemplateView):
    """AI Recommendations page view."""
    template_name = 'ai_recommendations/recommendations.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get recommendations for the current user if authenticated and is a student
        if self.request.user.is_authenticated and hasattr(self.request.user, 'role') and self.request.user.role == 'STUDENT':
            recommendations = CourseRecommendation.objects.filter(
                student=self.request.user
            ).select_related('course').order_by('-score', '-created_at')[:10]
            
            context['recommendations'] = recommendations
            context['has_recommendations'] = recommendations.exists()
        else:
            context['recommendations'] = []
            context['has_recommendations'] = False
        
        return context


ai_recommendations = AIRecommendationsView.as_view()
