import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
# This must happen before configuring the Celery app instance.
# We check which settings file to use based on an environment variable.
# Default to 'local' if not specified.
settings_module = os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{{ cookiecutter.project_slug }}.settings.local')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

app = Celery('{{ cookiecutter.project_slug }}')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """A sample task for debugging purposes."""
    print(f'Request: {self.request!r}')

# Optional: Add periodic tasks using Celery Beat schedule
# from celery.schedules import crontab
# app.conf.beat_schedule = {
#     'add-every-30-seconds': {
#         'task': 'myapp.tasks.add', # Replace with your actual task path
#         'schedule': 30.0,
#         'args': (16, 16)
#     },
#     'multiply-every-monday-morning': {
#        'task': 'myapp.tasks.multiply', # Replace with your actual task path
#        'schedule': crontab(hour=7, minute=30, day_of_week=1),
#        'args': (5, 5),
#     },
# }
# Remember to configure the beat scheduler in settings (already done in base.py)
# CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler' 