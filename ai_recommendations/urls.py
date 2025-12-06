from django.urls import path
from .views import ai_recommendations

app_name = 'ai_recommendations'

urlpatterns = [
    path('', ai_recommendations, name='recommendations'),
]
