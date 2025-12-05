from django.apps import AppConfig

class AIRecommendationsConfig(AppConfig):
    name = "ai_recommendations"
    verbose_name = "AI Recommendations"

    def ready(self):
        # Import signals here (local import to avoid side effects during management commands)
        try:
            from . import signals  # noqa: F401
        except Exception:
            # Avoid failing during migrations if signals have issues
            pass
