from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ProjXeemit.settings')

from django.conf import settings
from django.utils import timezone as datetime

app = Celery('XeemitTasks')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings')

app.conf.update(
    CELERYBEAT_SCHEDULE={
        'update-currency-rates-every-60s': {
            'task': 'Xeemit.tasks.update_currency_rates',
            'schedule': datetime.timedelta(minutes=60),
            'args': ()
        },
    },
    CELERY_TIMEZONE='UTC',
)

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


# celery -A ProjXeemit beat
# celery -A ProjXeemit worker -l info