from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from .models import CourseRecommendation, RecommendationFeedback
from authentication.models import User
from courses.models import Course
