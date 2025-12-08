from django.urls import path
from .views import course_catalog, course_details_modal

app_name = 'courses'

urlpatterns = [
    path('catalog/', course_catalog, name='catalog'),
    path('course-details/<int:section_id>/', course_details_modal, name='course-details'),
]
