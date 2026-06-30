import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oghie.settings')

application = get_wsgi_application()

from django.core.management import call_command
call_command('migrate', '--no-input', verbosity=0)
call_command('collectstatic', '--no-input', verbosity=0)
