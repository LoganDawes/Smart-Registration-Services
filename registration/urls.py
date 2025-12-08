from django.urls import path
from .views import (
    registration_page, 
    load_plan_form, 
    load_plan_to_cart, 
    add_to_cart, 
    remove_from_cart,
    confirm_all_registration
)
from django.views.generic import TemplateView

app_name = 'registration'

urlpatterns = [
    path('register/', registration_page, name='register'),
    path('search-courses/', TemplateView.as_view(template_name='registration/course_search_modal.html'), name='search-courses'),
    path('request-form/', TemplateView.as_view(template_name='registration/request_form_modal.html'), name='request-form'),
    path('load-plan-form/', load_plan_form, name='load-plan-form'),
    path('load-plan/<int:plan_id>/', load_plan_to_cart, name='load-plan'),
    path('add-to-cart/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/', remove_from_cart, name='remove-from-cart'),
    path('confirm-all/', confirm_all_registration, name='confirm-all'),
]
