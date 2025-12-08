from django.urls import path
from django.views.generic import RedirectView, TemplateView
from .views import (
    registration_page, 
    load_plan_form, 
    load_plan_to_added_courses, 
    add_to_added_courses, 
    remove_from_added_courses,
    confirm_all_registration
)

app_name = 'registration'

urlpatterns = [
    path('register/', registration_page, name='register'),
    path('search-courses/', TemplateView.as_view(template_name='registration/course_search_modal.html'), name='search-courses'),
    path('request-form/', TemplateView.as_view(template_name='registration/request_form_modal.html'), name='request-form'),
    path('load-plan-form/', load_plan_form, name='load-plan-form'),
    path('load-plan/<int:plan_id>/', load_plan_to_added_courses, name='load-plan'),
    path('add-to-added-courses/', add_to_added_courses, name='add-to-added-courses'),
    path('remove-from-added-courses/', remove_from_added_courses, name='remove-from-added-courses'),
    path('confirm-all/', confirm_all_registration, name='confirm-all'),
    # Legacy redirects (301 permanent)
    path('add-to-cart/', RedirectView.as_view(pattern_name='registration:add-to-added-courses', permanent=True)),
    path('remove-from-cart/', RedirectView.as_view(pattern_name='registration:remove-from-added-courses', permanent=True)),
    path('load-plan-to-cart/<int:plan_id>/', RedirectView.as_view(pattern_name='registration:load-plan', permanent=True)),
]
