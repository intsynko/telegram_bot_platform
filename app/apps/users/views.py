from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request

from apps.users.serializers import RegisterSerializer, UserSerializer
from apps.users.logic import facades, selectors


class AuthViewSet(viewsets.ViewSet):
    """ViewSet для аутентификации пользователей"""
    
    @action(detail=False, methods=['post'])
    def register(self, request: Request) -> Response:
        """Регистрация нового пользователя"""
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            user = facades.register_user(email, password)
            facades.login_user_session(request, user)
            
            return Response(UserSerializer(user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def login(self, request: Request) -> Response:
        """Логин пользователя"""
        email = request.data.get('email')
        password = request.data.get('password')
        
        user = facades.authenticate_user(email, password)
        if user:
            facades.login_user_session(request, user)
            return Response(UserSerializer(user).data)
        
        return Response(
            {'error': 'Invalid credentials'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['post'])
    def logout(self, request: Request) -> Response:
        """Выход пользователя из системы"""
        facades.logout_user_session(request)
        return Response({'success': True})


class UserViewSet(viewsets.ViewSet):
    """ViewSet для управления профилем пользователя"""
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def me(self, request: Request) -> Response:
        """Получить профиль текущего пользователя"""
        profile_data = selectors.get_user_profile(request.user)
        return Response(profile_data)