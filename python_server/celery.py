from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'python_server.settings')

app = Celery('python_server', broker='amqp://guest:guest@rabbitmq_server:5672//')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()