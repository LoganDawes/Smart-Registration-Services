from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'

    def ready(self):
        # Import signal handlers to ensure they're registered
        try:
            from . import signals  # noqa: F401
        except Exception:
            # Avoid hard failure during migrations or when signals import fails
            pass
