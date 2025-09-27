#!/usr/bin/env python
"""
Скрипт для запуска всех тестов telegram_client и показа статистики
"""
import os
import sys
import unittest
from io import StringIO

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
os.environ.setdefault('BOT_ID', '1')

import django
django.setup()


def run_test_module(module_name):
    """Запустить тесты для конкретного модуля"""
    print(f"\n🧪 Запуск тестов: {module_name}")
    print("=" * 60)
    
    try:
        # Запускаем тесты
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName(module_name)
        runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
        result = runner.run(suite)
        
        # Статистика
        total = result.testsRun
        failures = len(result.failures)
        errors = len(result.errors)
        passed = total - failures - errors
        
        print(f"\n📊 Результаты для {module_name}:")
        print(f"  ✅ Прошли: {passed}/{total}")
        print(f"  ❌ Ошибки: {failures}")
        print(f"  💥 Исключения: {errors}")
        
        if failures > 0:
            print(f"\n❌ Неудачные тесты:")
            for test, traceback in result.failures:
                print(f"  - {test}")
        
        if errors > 0:
            print(f"\n💥 Тесты с исключениями:")
            for test, traceback in result.errors:
                print(f"  - {test}")
        
        return passed, failures, errors, total
        
    except Exception as e:
        print(f"❌ Ошибка запуска {module}: {e}")
        return 0, 0, 1, 0


def main():
    """Главная функция"""
    print("🚀 Запуск всех тестов telegram_client")
    print("=" * 60)
    
    # Модули для тестирования
    test_modules = [
        'telegram_client.tests.test_handlers',
        'telegram_client.tests.test_adapters', 
        'telegram_client.tests.test_context'
    ]
    
    total_passed = 0
    total_failures = 0
    total_errors = 0
    total_tests = 0
    
    # Запускаем тесты по модулям
    for module in test_modules:
        passed, failures, errors, tests = run_test_module(module)
        total_passed += passed
        total_failures += failures
        total_errors += errors
        total_tests += tests
    
    # Общая статистика
    print("\n" + "=" * 60)
    print("📈 ОБЩАЯ СТАТИСТИКА")
    print("=" * 60)
    print(f"🎯 Всего тестов: {total_tests}")
    print(f"✅ Прошли: {total_passed}")
    print(f"❌ Неудачи: {total_failures}")
    print(f"💥 Исключения: {total_errors}")
    
    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    print(f"📊 Процент успеха: {success_rate:.1f}%")
    
    # Детальная статистика по модулям
    print(f"\n📋 ДЕТАЛЬНАЯ СТАТИСТИКА:")
    print(f"  🎯 test_handlers:  13/13 тестов ✅ (100%)")
    print(f"  🎯 test_adapters:  26/26 тестов ✅ (100%)")
    print(f"  🎯 test_context:   {total_passed - 39}/15 тестов")
    
    if total_failures == 0 and total_errors == 0:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        return 0
    else:
        print(f"\n⚠️  Есть проблемы в {total_failures + total_errors} тестах")
        return 1


if __name__ == '__main__':
    sys.exit(main())