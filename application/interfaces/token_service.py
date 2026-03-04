from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Tuple
from uuid import UUID


class TokenService(ABC):
    """Интерфейс для работы с токенами"""
    
    @abstractmethod
    def create_access_token(self, user_id: UUID, roles: list, 
                           permissions: dict = None) -> Tuple[str, int]:
        """Создать access token"""
        pass
    
    @abstractmethod
    def create_refresh_token(self, user_id: UUID) -> Tuple[str, int]:
        """Создать refresh token"""
        pass
    
    @abstractmethod
    def create_email_verification_token(self, user_id: UUID, email: str) -> str:
        """Создать токен для подтверждения email"""
        pass
    
    @abstractmethod
    def create_password_reset_token(self, user_id: UUID, email: str) -> str:
        """Создать токен для сброса пароля"""
        pass
    
    @abstractmethod
    def verify_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Проверить access token"""
        pass
    
    @abstractmethod
    def verify_refresh_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Проверить refresh token"""
        pass
    
    @abstractmethod
    def verify_email_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Проверить токен подтверждения email"""
        pass
    
    @abstractmethod
    def verify_password_reset_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Проверить токен сброса пароля"""
        pass