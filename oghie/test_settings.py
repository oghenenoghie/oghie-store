import importlib
import os
from unittest import mock

from django.test import SimpleTestCase

from oghie import settings as settings_module


class ServerlessConnectionPoolingTests(SimpleTestCase):
    """Guards against regressing to persistent DB connections on Vercel.

    Persistent connections (CONN_MAX_AGE > 0) held by short-lived serverless
    invocations exhausted Supabase's session-pooler connection cap and took
    down /api/products/ with "max clients reached in session mode".
    """

    def tearDown(self):
        importlib.reload(settings_module)

    def test_conn_max_age_is_zero_on_vercel(self):
        with mock.patch.dict(os.environ, {'VERCEL': '1', 'DATABASE_URL': 'sqlite:///test.db'}):
            importlib.reload(settings_module)
            self.assertEqual(settings_module.DATABASES['default']['CONN_MAX_AGE'], 0)

    def test_conn_max_age_is_nonzero_off_vercel(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop('VERCEL', None)
            importlib.reload(settings_module)
            self.assertEqual(settings_module.DATABASES['default']['CONN_MAX_AGE'], 600)
