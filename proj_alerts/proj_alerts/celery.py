from __future__ import absolute_import
import os

from celery import Celery

from proj_alerts import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj_alerts.settings')
app = Celery('proj_alerts')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

