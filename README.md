# Telegram Bot Master

Система управления Telegram ботами с веб-интерфейсом и конструктором сценариев.

## Развернуть локально

### 1. Запустить базу данных

```bash
docker run -d \
  --name tg-bot-db \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=db \
  -p 5432:5432 \
  postgres:15
```

### 2. Запустить приложение

```bash
docker run -d \
  -p 80:80 \
  -e DATABASE_URL=psql://user:password@host.docker.internal:5432/db \
  -e SECRET_KEY=your-secret-key \
  -e SYSTEM_BOT_TOKEN=your-telegram-bot-token \
  intsynko1/tg_bot_master:latest
```

Открыть в браузере: `http://localhost`

### Переменные окружения

| Переменная | Описание | Пример                          |
|---|---|---------------------------------|
| `DATABASE_URL` | Строка подключения к PostgreSQL | `psql://user:pass@host.docker.internal:5432/db` |
| `SECRET_KEY` | Секретный ключ Django (любая случайная строка) | `my-secret-key-123`             |
| `SYSTEM_BOT_TOKEN` | Токен системного Telegram бота | `123456:ABC-DEF...`             |
| `API_URL` | URL API если backend на другом хосте | `https://myserver.com`          |

> На macOS/Windows для подключения к postgres на хост-машине используй `host.docker.internal` вместо `localhost`.


## Разработка

### Быстрый старт

```bash
# Запуск БД
docker-compose up -d db

# Установка зависимостей и миграции
pip install -r requirements.txt
python app/manage.py migrate

# Запуск backend
python app/manage.py runserver

# Запуск frontend (в отдельном терминале)
cd web_app && npm install && npm start
```
