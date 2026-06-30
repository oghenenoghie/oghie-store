from django.db import migrations


def create_roles_and_profiles(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    User = apps.get_model('auth', 'User')
    UserProfile = apps.get_model('users', 'UserProfile')

    roles = {
        'Super Admin': 'super_admin',
        'Staff': 'staff',
        'Vendor': 'vendor',
        'Customer': 'customer',
    }

    groups = {name: Group.objects.get_or_create(name=name)[0] for name in roles}

    for user in User.objects.all():
        if user.is_superuser:
            role = 'super_admin'
            group = groups['Super Admin']
        elif user.is_staff:
            role = 'staff'
            group = groups['Staff']
        else:
            role = 'customer'
            group = groups['Customer']

        UserProfile.objects.get_or_create(user=user, defaults={'role': role})
        user.groups.add(group)


def remove_roles(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=['Super Admin', 'Staff', 'Vendor', 'Customer']).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(create_roles_and_profiles, remove_roles),
    ]
