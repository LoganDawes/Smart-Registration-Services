from django.urls import path
from .views import registration_page

app_name = 'registration'

urlpatterns = [
    path('', registration_page, name='register'),
]
