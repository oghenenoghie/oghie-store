import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oghie.settings')

application = get_wsgi_application()

# Run migrations automatically on cold start (safe — migrate is idempotent)
from django.core.management import call_command
call_command('migrate', '--no-input', verbosity=0)
