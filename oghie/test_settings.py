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


class SupabasePoolerPortTests(SimpleTestCase):
    """Guards against silently regressing to Supabase's session pooler.

    Production intermittently 500'd across /api/products/, register, login,
    and the admin with "max clients reached in session mode" because
    DATABASE_URL pointed at Supabase's session pooler (port 5432, capped at
    15 concurrent clients) instead of the transaction pooler (port 6543).
    """

    def tearDown(self):
        importlib.reload(settings_module)

    def test_supabase_session_pooler_port_is_rewritten_to_transaction_pooler(self):
        url = 'postgres://user:pass@aws-1-ap-southeast-2.pooler.supabase.com:5432/postgres'
        with mock.patch.dict(os.environ, {'DATABASE_URL': url}):
            importlib.reload(settings_module)
            self.assertEqual(settings_module.DATABASES['default']['PORT'], 6543)

    def test_transaction_pooler_port_is_left_alone(self):
        url = 'postgres://user:pass@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres'
        with mock.patch.dict(os.environ, {'DATABASE_URL': url}):
            importlib.reload(settings_module)
            self.assertEqual(settings_module.DATABASES['default']['PORT'], 6543)

    def test_non_supabase_postgres_host_on_5432_is_left_alone(self):
        url = 'postgres://user:pass@localhost:5432/postgres'
        with mock.patch.dict(os.environ, {'DATABASE_URL': url}):
            importlib.reload(settings_module)
            self.assertEqual(settings_module.DATABASES['default']['PORT'], 5432)


class CloudinaryUrlConfigTests(SimpleTestCase):
    """Guards against a malformed CLOUDINARY_URL crashing every request.

    The cloudinary package parses CLOUDINARY_URL at import time and raises
    ValueError for anything not starting with 'cloudinary://'. Since that
    import happens during django.setup(), a bad value (e.g. one missing the
    scheme) took down the entire site with a 500, including static assets.
    """

    def tearDown(self):
        importlib.reload(settings_module)

    def test_malformed_cloudinary_url_is_ignored(self):
        with mock.patch.dict(os.environ, {'CLOUDINARY_URL': 'api_key:api_secret@cloud_name'}):
            importlib.reload(settings_module)
            self.assertNotIn('cloudinary', settings_module.INSTALLED_APPS)
            self.assertNotIn('cloudinary_storage', settings_module.INSTALLED_APPS)

    def test_wellformed_cloudinary_url_enables_cloudinary_storage(self):
        with mock.patch.dict(os.environ, {'CLOUDINARY_URL': 'cloudinary://api_key:api_secret@cloud_name'}):
            importlib.reload(settings_module)
            self.assertIn('cloudinary', settings_module.INSTALLED_APPS)
            self.assertIn('cloudinary_storage', settings_module.INSTALLED_APPS)
            self.assertEqual(
                settings_module.STORAGES['default']['BACKEND'],
                'cloudinary_storage.storage.MediaCloudinaryStorage',
            )

    def test_missing_cloudinary_url_falls_back_to_default_storage(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop('CLOUDINARY_URL', None)
            importlib.reload(settings_module)
            self.assertNotIn('cloudinary', settings_module.INSTALLED_APPS)
