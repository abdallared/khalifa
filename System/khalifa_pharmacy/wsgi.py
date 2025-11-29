"""
WSGI config for khalifa_pharmacy project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')

application = get_wsgi_application()

