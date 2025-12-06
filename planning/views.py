from django.shortcuts import render
from django.views.generic import TemplateView


class SchedulePlanningView(TemplateView):
    """Schedule Planning page view."""
    template_name = 'planning/schedule.html'


schedule_planning = SchedulePlanningView.as_view()
