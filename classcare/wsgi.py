"""
WSGI config for ClassCare chatbot project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'classcare.settings')

application = get_wsgi_application()


