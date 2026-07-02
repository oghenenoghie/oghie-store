import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oghie.settings')

django.setup()

from django.core.management import call_command
call_command('migrate', '--no-input', verbosity=0)
call_command('collectstatic', '--no-input', verbosity=0)

# WhiteNoiseMiddleware snapshots STATIC_ROOT when the WSGI app is built, so
# collectstatic must populate /tmp/staticfiles (empty on every cold
# container) before get_wsgi_application() constructs the middleware stack -
# otherwise static assets 404 until the next cold start.
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
