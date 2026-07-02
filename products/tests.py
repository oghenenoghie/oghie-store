from rest_framework import status
from rest_framework.test import APITestCase

from .models import Category, Product


class ProductDetailLookupTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Apparel', slug='apparel')
        self.product = Product.objects.create(
            category=self.category,
            name='Classic T-Shirt',
            slug='classic-t-shirt',
            description='Soft cotton t-shirt.',
            price='29.99',
        )

    def test_retrieve_by_slug(self):
        response = self.client.get(f'/api/products/{self.product.slug}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.product.id)

    def test_retrieve_by_id(self):
        response = self.client.get(f'/api/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['slug'], self.product.slug)

    def test_retrieve_missing_slug_returns_404(self):
        response = self.client.get('/api/products/does-not-exist/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
