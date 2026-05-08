from decimal import Decimal

from django.db import migrations


def create_default_currencies(apps, schema_editor):
    Currency = apps.get_model('products', 'Currency')
    defaults = [
        ('USD', 'US Dollar', '$', Decimal('1.000000'), True),
        ('SAR', 'Saudi Riyal', 'SAR', Decimal('3.750000'), False),
        ('NGN', 'Nigerian Naira', '₦', Decimal('1400.000000'), False),
        ('EUR', 'Euro', '€', Decimal('0.930000'), False),
    ]

    for code, name, symbol, rate, is_base in defaults:
        Currency.objects.get_or_create(
            code=code,
            defaults={
                'name': name,
                'symbol': symbol,
                'exchange_rate_to_base': rate,
                'is_base': is_base,
                'is_active': True,
            },
        )


def remove_default_currencies(apps, schema_editor):
    Currency = apps.get_model('products', 'Currency')
    Currency.objects.filter(code__in=['USD', 'SAR', 'NGN', 'EUR']).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('products', '0004_currency_product_currency_productreview_wishlistitem'),
    ]

    operations = [
        migrations.RunPython(create_default_currencies, remove_default_currencies),
    ]
