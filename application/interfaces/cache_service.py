from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from uuid import UUID

from domain.entities.user import UserEntity


class CacheService(ABC):
    """Интерфейс для кэширования"""
    
    @abstractmethod
    async def get_user(self, user_id: UUID) -> Optional[UserEntity]:
        """Получить пользователя из кэша"""
        pass
    
    @abstractmethod
    async def set_user(self, user: UserEntity, ttl: int = 3600) -> None:
        """Сохранить пользователя в кэш"""
        pass
    
    @abstractmethod
    async def delete_user(self, user_id: UUID) -> None:
        """Удалить пользователя из кэша"""
        pass
    
    @abstractmethod
    async def get_refresh_token(self, user_id: UUID) -> Optional[str]:
        """Получить refresh token"""
        pass
    
    @abstractmethod
    async def set_refresh_token(self, user_id: UUID, token: str, ttl: int) -> None:
        """Сохранить refresh token"""
        pass
    
    @abstractmethod
    async def delete_refresh_token(self, user_id: UUID) -> None:
        """Удалить refresh token"""
        pass
    
    @abstractmethod
    async def get_password_reset_token(self, user_id: UUID) -> Optional[str]:
        """Получить токен сброса пароля"""
        pass
    
    @abstractmethod
    async def set_password_reset_token(self, user_id: UUID, token: str, ttl: int) -> None:
        """Сохранить токен сброса пароля"""
        pass
    
    @abstractmethod
    async def delete_password_reset_token(self, user_id: UUID) -> None:
        """Удалить токен сброса пароля"""
        pass