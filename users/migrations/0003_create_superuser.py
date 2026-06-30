import os
from django.db import migrations


def create_superuser(apps, schema_editor):
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'oghie.c@outlook.com')
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'oghie.c@outlook.com')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '@@oghieStore')

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
