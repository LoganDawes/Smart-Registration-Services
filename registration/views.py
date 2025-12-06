from django.shortcuts import render
from django.views.generic import TemplateView


class RegistrationView(TemplateView):
    """Registration page view."""
    template_name = 'registration/register.html'


registration_page = RegistrationView.as_view()
