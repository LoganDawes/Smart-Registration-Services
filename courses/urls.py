from django.urls import path
from .views import course_catalog

app_name = 'courses'

urlpatterns = [
    path('catalog/', course_catalog, name='catalog'),
]
