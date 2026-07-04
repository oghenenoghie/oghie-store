from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Category, Currency, Product, ProductImage, validate_image_upload_or_url


class ProductCategoryFilterTests(APITestCase):
    def setUp(self):
        self.currency = Currency.objects.get(code='USD')
        self.women = Category.objects.create(name='Women', slug='women')
        self.women_outerwear = Category.objects.create(
            name='Outerwear', slug='women-outerwear', parent=self.women,
        )
        self.men = Category.objects.create(name='Men', slug='men')

        self.coat = Product.objects.create(
            name='Coat', slug='coat', description='A coat', price='100.00',
            currency=self.currency, category=self.women_outerwear, stock_quantity=5,
        )
        self.shirt = Product.objects.create(
            name='Shirt', slug='shirt', description='A shirt', price='50.00',
            currency=self.currency, category=self.men, stock_quantity=5,
        )

    # Regression test: filtering by a parent category's slug ("women") only
    # matched products filed directly under that exact category - a product
    # filed under a subcategory like "women-outerwear" was invisible from
    # the parent's product listing, even though the mega-menu links to both
    # the parent ("Women") and its subcategories ("Outerwear").
    def test_filtering_by_parent_slug_includes_subcategory_products(self):
        response = self.client.get('/api/products/', {'category': 'women'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        slugs = {p['slug'] for p in response.data}
        self.assertIn('coat', slugs)
        self.assertNotIn('shirt', slugs)

    def test_filtering_by_subcategory_slug_excludes_other_categories(self):
        response = self.client.get('/api/products/', {'category': 'women-outerwear'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        slugs = {p['slug'] for p in response.data}
        self.assertEqual(slugs, {'coat'})


class ProductImageValidationTests(APITestCase):
    def setUp(self):
        currency = Currency.objects.get(code='USD')
        category = Category.objects.create(name='Test Category', slug='test-category')
        self.product = Product.objects.create(
            name='Coat', slug='validation-coat', description='A coat', price='100.00',
            currency=currency, category=category, stock_quantity=5,
        )

    # Regression test: ProductImage.image sometimes holds an external URL
    # (e.g. a stock-photo CDN link) instead of an uploaded file, and those
    # never have a recognizable file extension. FileExtensionValidator
    # rejected them outright, which blocked saving that row in the admin
    # entirely - even edits unrelated to the image - until it was replaced
    # with a real upload.
    def test_external_url_passes_validation(self):
        validate_image_upload_or_url(_FakeFile('https://images.example.com/photos/123456'))

    def test_real_upload_with_disallowed_extension_still_rejected(self):
        with self.assertRaises(ValidationError):
            validate_image_upload_or_url(_FakeFile('malware.exe'))

    def test_real_upload_with_allowed_extension_passes(self):
        validate_image_upload_or_url(_FakeFile('photo.jpg'))

    def test_product_image_with_url_saves_successfully(self):
        image = ProductImage.objects.create(
            product=self.product,
            image='https://images.example.com/photos/123456',
            alt_text='Coat',
            is_primary=True,
        )
        image.full_clean()


class _FakeFile:
    """Minimal stand-in for a Django File/FieldFile - the validator only
    reads .name."""

    def __init__(self, name):
        self.name = name
