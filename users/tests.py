from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import UserProfile


class RegisterViewTests(APITestCase):
    def test_register_creates_user_and_returns_tokens(self):
        url = reverse('users:register')
        response = self.client.post(url, {
            'username': 'newcustomer',
            'email': 'newcustomer@example.com',
            'password': 'S3cure-Passw0rd!',
            'phone': '+15551234567',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

        user = get_user_model().objects.get(username='newcustomer')
        self.assertTrue(user.check_password('S3cure-Passw0rd!'))
        self.assertEqual(user.profile.role, UserProfile.Role.CUSTOMER)
        self.assertEqual(user.profile.phone, '+15551234567')

    def test_register_rejects_duplicate_username(self):
        get_user_model().objects.create_user(username='taken', password='S3cure-Passw0rd!')
        url = reverse('users:register')
        response = self.client.post(url, {
            'username': 'taken',
            'email': 'other@example.com',
            'password': 'S3cure-Passw0rd!',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_rejects_weak_password(self):
        url = reverse('users:register')
        response = self.client.post(url, {
            'username': 'weakpassworduser',
            'email': 'weak@example.com',
            'password': '123',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
