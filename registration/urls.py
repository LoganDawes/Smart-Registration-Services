from django.urls import path
from .views import registration_page
from django.views.generic import TemplateView

app_name = 'registration'

urlpatterns = [
    path('', registration_page, name='register'),
    path('search-courses/', TemplateView.as_view(template_name='registration/course_search_modal.html'), name='search-courses'),
    path('request-form/', TemplateView.as_view(template_name='registration/request_form_modal.html'), name='request-form'),
]
