import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oghie.settings')

django.setup()

# vercel.json's buildCommand already runs migrate at build time, so this
# only needs to (re)populate /tmp/staticfiles, which is wiped on every cold
# container. Running migrate here too would make every cold start (not just
# deploys) depend on a live DB connection - a transient DB hiccup (pooler
# exhaustion, brief network blip) would then crash the whole app, since this
# runs before the WSGI application object exists.
from django.core.management import call_command
call_command('collectstatic', '--no-input', verbosity=0)

# WhiteNoiseMiddleware snapshots STATIC_ROOT when the WSGI app is built, so
# collectstatic must populate /tmp/staticfiles (empty on every cold
# container) before get_wsgi_application() constructs the middleware stack -
# otherwise static assets 404 until the next cold start.
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
