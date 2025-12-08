from django.urls import path
from .views import schedule_planning, select_plan_form
from django.views.generic import TemplateView

app_name = 'planning'

urlpatterns = [
    path('schedule/', schedule_planning, name='schedule'),
    path('create-plan-form/', TemplateView.as_view(template_name='planning/create_plan_modal.html'), name='create-plan-form'),
    path('select-plan-form/', select_plan_form, name='select-plan-form'),
]
