from django.apps import AppConfig

class PollsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'polls'
    
    def ready(self):
        import polls.signals  # Import signals
        import polls.tasks    # Import tasks to ensure they're registered