from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.generic import TemplateView

# from .models import CourseRecommendation
# Use these if you need login/permission checks:
# from django.contrib.auth.decorators import login_required


class AIRecommendationsView(TemplateView):
    """AI Recommendations page view."""
    template_name = 'ai_recommendations/recommendations.html'


ai_recommendations = AIRecommendationsView.as_view()
