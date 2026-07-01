import os
from django.db import migrations


def create_superuser(apps, schema_editor):
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
    if not password:
        # No hardcoded fallback: skip silently so `migrate` still succeeds
        # without accidentally provisioning an admin account with a known password.
        return

    username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'oghie.c@outlook.com')
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'oghie.c@outlook.com')

    User = apps.get_model('auth', 'User')
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_create_roles_and_profiles'),
    ]

    operations = [
        migrations.RunPython(create_superuser, migrations.RunPython.noop),
    ]
