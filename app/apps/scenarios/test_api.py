"""
API тесты для приложения scenarios
Фиксируют текущее поведение API перед рефакторингом
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.scenarios.models import Scenario

User = get_user_model()


class ScenarioAPITestCase(APITestCase):
    """Тесты API для управления сценариями"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password='testpassword123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.scenario_data = {
            'name': 'Test Scenario',
            'graph': {
                'nodes': [
                    {'id': '1', 'type': 'start', 'data': {'text': 'Hello'}},
                    {'id': '2', 'type': 'message', 'data': {'text': 'How are you?'}}
                ],
                'edges': [
                    {'source': '1', 'target': '2'}
                ]
            }
        }

    def test_create_scenario_success(self):
        """Тест успешного создания сценария"""
        response = self.client.post('/api/scenarios/', self.scenario_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], self.scenario_data['name'])
        
        # Проверяем, что сценарий создался в БД с правильным владельцем
        scenario = Scenario.objects.get(id=response.data['id'])
        self.assertEqual(scenario.owner, self.user)
        self.assertFalse(scenario.is_template)

    def test_list_user_scenarios_only(self):
        """Тест получения списка сценариев только текущего пользователя"""
        # Создаем сценарии для текущего пользователя
        scenario1 = Scenario.objects.create(
            name='User Scenario 1', 
            owner=self.user,
            is_template=False
        )
        scenario2 = Scenario.objects.create(
            name='User Scenario 2', 
            owner=self.user,
            is_template=False
        )
        
        # Создаем сценарий для другого пользователя
        other_user = User.objects.create_user(
            username='other@example.com',
            email='other@example.com',
            password='password'
        )
        Scenario.objects.create(
            name='Other User Scenario', 
            owner=other_user,
            is_template=False
        )
        
        # Создаем шаблон (не должен показываться в обычном списке)
        Scenario.objects.create(
            name='Template Scenario',
            owner=self.user,
            is_template=True
        )
        
        response = self.client.get('/api/scenarios/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Только сценарии текущего пользователя
        
        scenario_names = [scenario['name'] for scenario in response.data]
        self.assertIn('User Scenario 1', scenario_names)
        self.assertIn('User Scenario 2', scenario_names)
        self.assertNotIn('Other User Scenario', scenario_names)
        self.assertNotIn('Template Scenario', scenario_names)

    def test_get_scenario_detail(self):
        """Тест получения детальной информации о сценарии"""
        scenario = Scenario.objects.create(
            name='Test Scenario',
            owner=self.user,
            graph=self.scenario_data['graph']
        )
        
        response = self.client.get(f'/api/scenarios/{scenario.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], scenario.id)
        self.assertEqual(response.data['name'], scenario.name)
        self.assertEqual(response.data['graph'], self.scenario_data['graph'])

    def test_update_scenario(self):
        """Тест обновления сценария"""
        scenario = Scenario.objects.create(
            name='Original Name',
            owner=self.user,
            graph={'nodes': [], 'edges': []}
        )
        
        updated_data = {
            'name': 'Updated Name',
            'graph': self.scenario_data['graph']
        }
        
        response = self.client.put(f'/api/scenarios/{scenario.id}/', updated_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], updated_data['name'])
        self.assertEqual(response.data['graph'], updated_data['graph'])
        
        # Проверяем обновление в БД
        scenario.refresh_from_db()
        self.assertEqual(scenario.name, updated_data['name'])

    def test_copy_template_scenario(self):
        """Тест копирования шаблонного сценария"""
        # Создаем шаблонный сценарий
        template = Scenario.objects.create(
            name='Template Scenario',
            owner=self.user,
            graph=self.scenario_data['graph'],
            is_template=True
        )
        
        response = self.client.post(f'/api/scenarios/{template.id}/copy/')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Template Scenario - Копия')
        self.assertEqual(response.data['graph'], self.scenario_data['graph'])
        
        # Проверяем, что создался новый сценарий
        copied_scenario = Scenario.objects.get(id=response.data['id'])
        self.assertEqual(copied_scenario.owner, self.user)
        self.assertFalse(copied_scenario.is_template)  # Копия не должна быть шаблоном

    def test_copy_non_template_scenario_fails(self):
        """Тест неудачного копирования несуществующего шаблона"""
        # Создаем обычный сценарий (не шаблон)
        regular_scenario = Scenario.objects.create(
            name='Regular Scenario',
            owner=self.user,
            is_template=False
        )
        
        response = self.client.post(f'/api/scenarios/{regular_scenario.id}/copy/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_scenario(self):
        """Тест удаления сценария"""
        scenario = Scenario.objects.create(
            name='To Delete',
            owner=self.user
        )
        
        response = self.client.delete(f'/api/scenarios/{scenario.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Scenario.objects.filter(id=scenario.id).exists())


class ScenarioTemplateAPITestCase(APITestCase):
    """Тесты API для шаблонов сценариев"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password='testpassword123'
        )
        # Для шаблонов аутентификация не требуется
        
    def test_list_template_scenarios_public_access(self):
        """Тест получения списка шаблонных сценариев без аутентификации"""
        # Создаем шаблонные сценарии
        template1 = Scenario.objects.create(
            name='Template 1',
            owner=self.user,
            is_template=True
        )
        template2 = Scenario.objects.create(
            name='Template 2', 
            owner=self.user,
            is_template=True
        )
        
        # Создаем обычный сценарий (не должен показываться)
        Scenario.objects.create(
            name='Regular Scenario',
            owner=self.user,
            is_template=False
        )
        
        response = self.client.get('/api/scenarios/template/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        template_names = [template['name'] for template in response.data]
        self.assertIn('Template 1', template_names)
        self.assertIn('Template 2', template_names)
        self.assertNotIn('Regular Scenario', template_names)

    def test_get_template_scenario_detail_public_access(self):
        """Тест получения детальной информации о шаблоне без аутентификации"""
        template = Scenario.objects.create(
            name='Template Scenario',
            owner=self.user,
            graph={'nodes': [{'id': '1', 'type': 'start'}], 'edges': []},
            is_template=True
        )
        
        response = self.client.get(f'/api/scenarios/template/{template.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], template.id)
        self.assertEqual(response.data['name'], template.name)
        self.assertEqual(response.data['graph'], template.graph)
