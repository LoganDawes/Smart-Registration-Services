from django.urls import path
from .views import schedule_planning

app_name = 'planning'

urlpatterns = [
    path('schedule/', schedule_planning, name='schedule'),
]
