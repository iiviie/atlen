# authentication/tests/test_models.py
from django.test import TestCase
from django.utils import timezone
from authentication.models import User, EmailVerificationToken
from datetime import timedelta

class UserModelTests(TestCase):
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
    def test_create_user(self):
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.email, self.user_data['email'])
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertFalse(user.is_active)
        self.assertFalse(user.email_verified)

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            email=self.user_data['email'],
            password=self.user_data['password']
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)
        self.assertTrue(user.email_verified)

# authentication/tests/test_views.py
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from authentication.models import User, EmailVerificationToken

class AuthenticationViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('authentication:register')
        self.login_url = reverse('authentication:login')
        self.user_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'confirm_password': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }

    def test_user_registration(self):
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=self.user_data['email']).exists())

    def test_user_login(self):
        # Create and verify user first
        user = User.objects.create_user(
            email=self.user_data['email'],
            password=self.user_data['password']
        )
        user.is_active = True
        user.email_verified = True
        user.save()

        response = self.client.post(self.login_url, {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)

# authentication/tests/test_serializers.py
from django.test import TestCase
from authentication.serializers import RegisterSerializer, LoginSerializer
from authentication.models import User

class SerializerTests(TestCase):
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'confirm_password': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }

    def test_valid_registration_serializer(self):
        serializer = RegisterSerializer(data=self.user_data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_password_match(self):
        invalid_data = self.user_data.copy()
        invalid_data['confirm_password'] = 'WrongPass123!'
        serializer = RegisterSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())