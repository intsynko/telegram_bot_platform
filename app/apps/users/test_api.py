"""
API тесты для приложения users
Фиксируют текущее поведение API перед рефакторингом
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class UserAuthAPITestCase(APITestCase):
    """Тесты аутентификации пользователей"""
    
    def setUp(self):
        self.register_url = '/api/users/auth/register/'
        self.login_url = '/api/users/auth/login/'
        self.user_url = '/api/users/auth/user/'
        self.logout_url = '/api/users/auth/logout/'
        
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }

    def test_register_user_success(self):
        """Тест успешной регистрации пользователя"""
        response = self.client.post(self.register_url, self.user_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['email'], self.user_data['email'])
        
        # Проверяем, что пользователь создался в БД
        user = User.objects.get(email=self.user_data['email'])
        self.assertEqual(user.username, self.user_data['email'])
        
        # Проверяем, что пользователь автоматически залогинен
        self.assertTrue('sessionid' in response.cookies or response.wsgi_request.user.is_authenticated)

    def test_register_user_invalid_data(self):
        """Тест регистрации с невалидными данными"""
        invalid_data = {'email': 'invalid-email', 'password': ''}
        response = self.client.post(self.register_url, invalid_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_login_user_success(self):
        """Тест успешного логина пользователя"""
        # Создаем пользователя
        user = User.objects.create_user(
            username=self.user_data['email'],
            email=self.user_data['email'],
            password=self.user_data['password']
        )
        
        response = self.client.post(self.login_url, self.user_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], user.id)
        self.assertEqual(response.data['email'], user.email)

    def test_login_user_invalid_credentials(self):
        """Тест логина с неверными учетными данными"""
        invalid_data = {
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(self.login_url, invalid_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid credentials')

    def test_get_user_profile_authenticated(self):
        """Тест получения профиля аутентифицированного пользователя"""
        user = User.objects.create_user(
            username=self.user_data['email'],
            email=self.user_data['email'],
            password=self.user_data['password']
        )
        self.client.force_authenticate(user=user)
        
        response = self.client.get(self.user_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], user.id)
        self.assertEqual(response.data['email'], user.email)

    def test_get_user_profile_unauthenticated(self):
        """Тест получения профиля неаутентифицированного пользователя"""
        response = self.client.get(self.user_url)
        
        # DRF возвращает 403 для session authentication
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_logout_user(self):
        """Тест выхода пользователя из системы"""
        user = User.objects.create_user(
            username=self.user_data['email'],
            email=self.user_data['email'],
            password=self.user_data['password']
        )
        self.client.force_authenticate(user=user)
        
        response = self.client.post(self.logout_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
