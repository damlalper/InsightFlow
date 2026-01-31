"""
ASGI config for InsightFlow project.
"""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insightflow.settings')

application = get_asgi_application()
