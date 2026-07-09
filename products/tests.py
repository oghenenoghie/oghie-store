from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from rest_framework import status
from rest_framework.test import APITestCase

from cms.models import CMSSection

from .models import Category, Currency, Product, ProductImage, ProductReview, validate_image_upload_or_url


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


class ProductListQueryCountTests(APITestCase):
    # Regression guard: ProductSerializer.get_average_rating/get_review_count
    # used to run their own `obj.reviews.filter(...)` queries per product
    # (get_average_rating alone re-evaluated that filtered queryset three
    # times), and currency wasn't select_related either - so listing N
    # products fired roughly 4N+ extra queries against the DB. Over a
    # serverless-to-Postgres network hop that turned a product list into a
    # multi-second response. This pins the query count so it can't silently
    # regress back to scaling with the number of products.
    def test_listing_products_uses_a_fixed_number_of_queries(self):
        currency = Currency.objects.get(code='USD')
        category = Category.objects.create(name='Query Count', slug='query-count')
        User = get_user_model()
        for i in range(5):
            product = Product.objects.create(
                name=f'Product {i}', slug=f'product-{i}', description='d', price='10.00',
                currency=currency, category=category, stock_quantity=5,
            )
            reviewer = User.objects.create_user(username=f'reviewer{i}', password='x')
            ProductReview.objects.create(
                product=product, user=reviewer, rating=5, status=ProductReview.Status.APPROVED,
            )

        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get('/api/products/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)
        self.assertLess(len(ctx.captured_queries), 10)


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


class SeedDemoDataTests(TestCase):
    # Regression guard: seed_demo_data used to generate solid-color PNG
    # squares as product/hero images instead of real photos. Confirms the
    # command now seeds a multi-slide hero carousel and gives every demo
    # product real (http) image URLs instead of a placeholder file.
    def test_seeds_multiple_ordered_hero_slides(self):
        call_command('seed_demo_data')

        heroes = list(
            CMSSection.objects.filter(section_type=CMSSection.SectionType.HERO).order_by('sort_order')
        )

        self.assertGreaterEqual(len(heroes), 2)
        self.assertEqual([h.sort_order for h in heroes], sorted(h.sort_order for h in heroes))
        for hero in heroes:
            self.assertTrue(hero.is_active)
            self.assertTrue(hero.image.name.startswith('https://'))

    def test_seeds_products_with_real_image_urls(self):
        call_command('seed_demo_data')

        product = Product.objects.filter(slug__startswith='demo-').first()
        self.assertIsNotNone(product)

        images = list(product.images.all())
        self.assertEqual(len(images), 2)
        for image in images:
            self.assertTrue(image.image.name.startswith('https://'))

    def test_running_twice_does_not_duplicate_hero_slides(self):
        call_command('seed_demo_data')
        call_command('seed_demo_data')

        hero_count = CMSSection.objects.filter(section_type=CMSSection.SectionType.HERO).count()
        self.assertEqual(hero_count, 4)
