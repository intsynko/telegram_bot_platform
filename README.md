# Telegram Bot Master

Система управления Telegram ботами с веб-интерфейсом и конструктором сценариев.

## 🏗️ Архитектура

- **Backend**: Django + DRF + PostgreSQL
- **Frontend**: React.js
- **Telegram Bot**: python-telegram-bot
- **Контейнеризация**: Docker + docker-compose

## 🚀 Быстрый старт

### Установка зависимостей

```bash
# Активация виртуального окружения
source venv/bin/activate

# Установка Python зависимостей
pip install -r requirements.txt

# Установка Node.js зависимостей (для фронтенда)
cd web_app
npm install
cd ..
```

### Настройка окружения

```bash
# Настройка переменных окружения
export DJANGO_SETTINGS_MODULE=server.settings
export BOT_ID=1
export SYSTEM_BOT_TOKEN=your_telegram_bot_token_here
```

### Запуск сервисов

```bash
# Запуск PostgreSQL (через Docker)
docker-compose up -d db

# Миграции Django
cd app
python manage.py migrate

# Запуск Django сервера
python manage.py runserver

# Запуск фронтенда (в отдельном терминале)
cd web_app
npm start
```

## 🧪 Тестирование

### Быстрый запуск всех тестов

```bash
# Переход в директорию приложения
cd app

# Активация виртуального окружения (если не активировано)
source ../venv/bin/activate

# Установка переменных окружения для тестов
export DJANGO_SETTINGS_MODULE=server.settings
export BOT_ID=1

# 🚀 ЗАПУСК ВСЕХ ТЕСТОВ ОДНОЙ КОМАНДОЙ
python run_all_tests.py
```

### Запуск тестов по отдельности

#### Django API тесты

```bash
cd app

# Все Django тесты (с сохранением тестовой БД для скорости)
python manage.py test --keepdb

# Тесты конкретного приложения
python manage.py test apps.users --keepdb
python manage.py test apps.bots --keepdb
python manage.py test apps.scenarios --keepdb
python manage.py test apps.chats --keepdb

# Конкретный тест-файл
python manage.py test apps.users.test_api --keepdb
python manage.py test apps.bots.test_api --keepdb
python manage.py test apps.scenarios.test_api --keepdb
python manage.py test apps.chats.test_api --keepdb

# Пересоздать тестовую БД (если нужно)
python manage.py test --debug-mode
```

#### Telegram Client тесты

```bash
cd app

# Все тесты telegram_client с красивой статистикой
python telegram_client/tests/run_tests.py

# Отдельные модули telegram_client
python -m unittest telegram_client.tests.test_handlers -v    # Хендлеры узлов сценария (13 тестов)
python -m unittest telegram_client.tests.test_adapters -v   # Адаптеры (26 тестов)
python -m unittest telegram_client.tests.test_context -v    # Контекстные функции (15 тестов)

# Конкретный тест
python -m unittest telegram_client.tests.test_handlers.TestHandlers.test_process_message_node -v
```

### Статистика тестов

**Django API тесты:**
- `apps.users.test_api` - 4 теста (аутентификация, CRUD пользователей)
- `apps.bots.test_api` - 4 теста (CRUD ботов, управление токенами)
- `apps.scenarios.test_api` - 4 теста (CRUD сценариев, валидация графов)
- `apps.chats.test_api` - 4 теста (чаты, сообщения, поля форм)

**Telegram Client тесты:**
- `test_handlers` - 13 тестов (все типы узлов сценария)
- `test_adapters` - 26 тестов (Telegram API, Django ORM, уведомления)
- `test_context` - 15 тестов (управление контекстом, сохранение данных)

**Всего: ~70 тестов**

## 🔧 Разработка

### Структура проекта

```
├── app/                          # Django приложение
│   ├── apps/                     # Django приложения
│   │   ├── users/               # Пользователи и аутентификация
│   │   ├── bots/                # Управление ботами
│   │   ├── scenarios/           # Сценарии и графы
│   │   └── chats/               # Чаты и сообщения
│   ├── telegram_client/         # Telegram бот логика
│   │   ├── handlers.py          # Обработчики узлов сценария
│   │   ├── adapters.py          # Адаптеры внешних сервисов
│   │   ├── context.py           # Управление контекстом
│   │   └── tests/               # Тесты telegram_client
│   └── server/                  # Настройки Django
├── web_app/                     # React фронтенд
└── db/                          # PostgreSQL данные
```

### Архитектурные слои

- **Presentation**: DRF ViewSets, React компоненты, Telegram handlers
- **Application**: Фасады (facades.py), селекторы (selectors.py)
- **Domain**: Django модели, бизнес-логика
- **Infrastructure**: ORM, внешние API, адаптеры

### Стандарты кода

- **Python**: Black, isort, flake8, mypy --strict
- **JavaScript**: ESLint, Prettier
- **Тестирование**: unittest, Django TestCase, React Testing Library
- **Документация**: Google-style docstrings

## 📚 API Документация

После запуска Django сервера доступна по адресу:
- Swagger UI: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`

## 🐳 Docker

```bash
# Запуск всего стека
docker-compose up

# Только база данных
docker-compose up -d db

# Пересборка контейнеров
docker-compose up --build
```

## 🔍 Отладка

### Логи

```bash
# Django логи
tail -f app/logs/django.log

# Telegram бот логи
tail -f app/logs/telegram.log

# PostgreSQL логи
docker-compose logs -f db
```

### Полезные команды

```bash
# Django shell
cd app && python manage.py shell

# Создание суперпользователя
cd app && python manage.py createsuperuser

# Сброс базы данных
cd app && python manage.py flush

# Создание миграций
cd app && python manage.py makemigrations

# Применение миграций
cd app && python manage.py migrate
```

## 🤝 Вклад в проект

1. Создайте ветку для новой функции
2. Напишите тесты для новой функциональности
3. Убедитесь, что все тесты проходят
4. Следуйте стандартам кодирования
5. Создайте Pull Request

## 📝 Лицензия

MIT License
