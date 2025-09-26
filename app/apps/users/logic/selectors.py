"""
Селекторы для запросов к БД приложения users
Содержат функции для получения данных пользователей
"""
from typing import Optional
from django.contrib.auth import get_user_model

User = get_user_model()


def get_user_by_email(email: str) -> Optional[User]:
    """Получить пользователя по email"""
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        return None


def get_user_profile(user: User) -> dict:
    """Получить данные профиля пользователя"""
    return {
        'id': user.id,
        'email': user.email,
        'username': user.username,
    }
