"""
WSGI config for Web_odontologia project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

try:
    import MySQLdb  # noqa: F401
except ImportError:
    import pymysql

    pymysql.install_as_MySQLdb()

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Web_odontologia.settings')

application = get_wsgi_application()
