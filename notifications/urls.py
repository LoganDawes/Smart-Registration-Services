from django.urls import path
from .views import notifications, send_test_notification, mark_notification_read

app_name = 'notifications'

urlpatterns = [
    path('', notifications, name='notifications'),
    path('send-test/', send_test_notification, name='send-test'),
    path('<int:notification_id>/mark-read/', mark_notification_read, name='mark-read'),
]
