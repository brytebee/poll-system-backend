import os
from celery import Celery

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'poll_system.settings.development')

app = Celery('poll_system')

# Configure Celery using settings from Django settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load tasks from all registered Django apps
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
