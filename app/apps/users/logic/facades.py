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
    user = User.objects.create_user(
        username=email,
        email=email,
        password=password
    )
    return user


def authenticate_user(email: str, password: str) -> Optional[User]:
    """Аутентификация пользователя по email/паролю"""
    return authenticate(username=email, password=password)


def login_user_session(request: HttpRequest, user: User) -> None:
    """Создание пользовательской сессии"""
    login(request, user)


def logout_user_session(request: HttpRequest) -> None:
    """Завершение пользовательской сессии"""
    logout(request)
