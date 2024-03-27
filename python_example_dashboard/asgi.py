import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'python_example_dashboard.settings')

application = get_asgi_application()
