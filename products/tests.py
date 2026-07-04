from rest_framework import status
from rest_framework.test import APITestCase

from .models import Category, Currency, Product


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
