from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import UserProfile


class RegisterViewTests(APITestCase):
    def setUp(self):
        self.url = reverse('users:register')

    def test_register_creates_user_and_profile(self):
        response = self.client.post(self.url, {
            'username': 'newcustomer',
            'email': 'newcustomer@example.com',
            'password': 'S0meStrongPass!',
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        User = get_user_model()
        user = User.objects.get(username='newcustomer')
        self.assertEqual(user.email, 'newcustomer@example.com')
        self.assertTrue(user.check_password('S0meStrongPass!'))
        self.assertEqual(user.profile.role, UserProfile.Role.CUSTOMER)
        self.assertNotIn('password', response.data)

    def test_register_rejects_duplicate_email(self):
        get_user_model().objects.create_user(
            username='existing', email='dupe@example.com', password='S0meStrongPass!'
        )

        response = self.client.post(self.url, {
            'username': 'anothername',
            'email': 'dupe@example.com',
            'password': 'S0meStrongPass!',
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_rejects_weak_password(self):
        response = self.client.post(self.url, {
            'username': 'weakpassuser',
            'email': 'weak@example.com',
            'password': '123',
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
