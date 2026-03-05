from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from domain.entities.refresh_token import RefreshTokenEntity

class RefreshTokenRepository(ABC):
    @abstractmethod
    async def save(self, token: RefreshTokenEntity) -> None:
        """Сохранить новый или обновить существующий токен"""
        pass

    @abstractmethod
    async def get_by_hash(self, token_hash: str) -> Optional[RefreshTokenEntity]:
        """Получить токен по хешу"""
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> List[RefreshTokenEntity]:
        """Получить все токены пользователя"""
        pass

    @abstractmethod
    async def delete(self, token: str) -> None:
        """Удалить конкретный токен"""
        pass

    @abstractmethod
    async def delete_by_id(self, id: str) -> None:
        """Удалить конкретный токен"""
        pass

    @abstractmethod
    async def delete_all_for_user(self, user_id: UUID) -> None:
        """Удалить все токены конкретного пользователя"""
        pass

    @abstractmethod
    async def revoke_expired(self) -> int:
        """Удалить все просроченные токены, вернуть количество удалённых"""
        pass