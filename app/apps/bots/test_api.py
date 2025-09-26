"""
API тесты для приложения bots
Фиксируют текущее поведение API перед рефакторингом
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch

from apps.bots.models import Bot
from apps.scenarios.models import Scenario

User = get_user_model()


class BotAPITestCase(APITestCase):
    """Тесты API для управления ботами"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password='testpassword123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.bot_data = {
            'name': 'Test Bot',
            'token': '123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ',
            'description': 'Test bot description'
        }
        
        self.scenario = Scenario.objects.create(
            name='Test Scenario',
            owner=self.user,
            graph={'nodes': [], 'edges': []}
        )

    def test_create_bot_success(self):
        """Тест успешного создания бота"""
        response = self.client.post('/api/bots/', self.bot_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], self.bot_data['name'])
        self.assertEqual(response.data['token'], self.bot_data['token'])
        
        # Проверяем, что бот создался в БД с правильным владельцем
        bot = Bot.objects.get(id=response.data['id'])
        self.assertEqual(bot.owner, self.user)

    def test_list_bots_for_authenticated_user(self):
        """Тест получения списка ботов для аутентифицированного пользователя"""
        # Создаем ботов для текущего пользователя
        bot1 = Bot.objects.create(name='Bot 1', token='token1', owner=self.user)
        bot2 = Bot.objects.create(name='Bot 2', token='token2', owner=self.user)
        
        # Создаем бота для другого пользователя
        other_user = User.objects.create_user(
            username='other@example.com',
            email='other@example.com',
            password='password'
        )
        Bot.objects.create(name='Other Bot', token='token3', owner=other_user)
        
        response = self.client.get('/api/bots/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Только боты текущего пользователя
        
        bot_names = [bot['name'] for bot in response.data]
        self.assertIn('Bot 1', bot_names)
        self.assertIn('Bot 2', bot_names)
        self.assertNotIn('Other Bot', bot_names)

    def test_get_bot_detail(self):
        """Тест получения детальной информации о боте"""
        bot = Bot.objects.create(
            name='Test Bot', 
            token='test_token', 
            owner=self.user,
            scenario=self.scenario
        )
        
        response = self.client.get(f'/api/bots/{bot.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], bot.id)
        self.assertEqual(response.data['name'], bot.name)
        self.assertIn('scenario', response.data)
        self.assertIn('is_running', response.data)

    @patch('apps.bots.views.start_bot')
    def test_run_bot_with_scenario(self, mock_start_bot):
        """Тест запуска бота со сценарием"""
        mock_start_bot.return_value = True
        
        bot = Bot.objects.create(
            name='Test Bot', 
            token='test_token', 
            owner=self.user,
            scenario=self.scenario
        )
        
        response = self.client.post(f'/api/bots/{bot.id}/run/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        mock_start_bot.assert_called_once_with(bot.id)

    def test_run_bot_without_scenario(self):
        """Тест запуска бота без сценария"""
        bot = Bot.objects.create(
            name='Test Bot', 
            token='test_token', 
            owner=self.user
        )
        
        response = self.client.post(f'/api/bots/{bot.id}/run/')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'No scenario selected')

    @patch('apps.bots.views.stop_bot')
    def test_stop_bot(self, mock_stop_bot):
        """Тест остановки бота"""
        mock_stop_bot.return_value = True
        
        bot = Bot.objects.create(
            name='Test Bot', 
            token='test_token', 
            owner=self.user
        )
        
        response = self.client.post(f'/api/bots/{bot.id}/stop/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        mock_stop_bot.assert_called_once_with(bot.id)

    def test_set_scenario_for_bot(self):
        """Тест привязки сценария к боту"""
        bot = Bot.objects.create(
            name='Test Bot', 
            token='test_token', 
            owner=self.user
        )
        
        response = self.client.post(
            f'/api/bots/{bot.id}/set_scenario/',
            {'scenario': self.scenario.id}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем, что сценарий привязался
        bot.refresh_from_db()
        self.assertEqual(bot.scenario, self.scenario)
        
        # Проверяем структуру ответа
        self.assertEqual(response.data['id'], bot.id)
        self.assertIn('scenario', response.data)
        self.assertEqual(response.data['scenario']['id'], self.scenario.id)

    def test_unauthenticated_access_denied(self):
        """Тест запрета доступа для неаутентифицированных пользователей"""
        self.client.force_authenticate(user=None)
        
        response = self.client.get('/api/bots/')
        # DRF возвращает 403 для session authentication
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        response = self.client.post('/api/bots/', self.bot_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
