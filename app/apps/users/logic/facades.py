"""
Фасады для бизнес-логики приложения users
Содержат функции для работы с пользователями и аутентификацией
"""
from typing import Optional
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.http import HttpRequest

User = get_user_model()


def register_user(email: str, password: str) -> User:
    """Регистрация нового пользователя"""
    # TODO: Реализовать в следующем этапе
    pass


def authenticate_user(email: str, password: str) -> Optional[User]:
    """Аутентификация пользователя по email/паролю"""
    # TODO: Реализовать в следующем этапе
    pass


def login_user_session(request: HttpRequest, user: User) -> None:
    """Создание пользовательской сессии"""
    # TODO: Реализовать в следующем этапе
    pass


def logout_user_session(request: HttpRequest) -> None:
    """Завершение пользовательской сессии"""
    # TODO: Реализовать в следующем этапе
    pass
