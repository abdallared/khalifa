"""
ASGI config for khalifa_pharmacy project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')

application = get_asgi_application()

