from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from domain.entities.user import UserEntity
from domain.entities.role import Role, RoleType


class UserEntityRepository(ABC):
    """Интерфейс репозитория для пользователей"""

    @abstractmethod
    async def get(self, id: UUID) -> Optional[UserEntity]:
        """Получить пользователя по ID"""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[UserEntity]:
        """Получить пользователя по email"""
        pass

    @abstractmethod
    async def add(self, user: UserEntity) -> None:
        """Добавить пользователя"""
        pass

    @abstractmethod
    async def update(self, user: UserEntity) -> None:
        """Обновить пользователя"""
        pass

    @abstractmethod
    async def delete(self, id: UUID) -> None:
        """Удалить пользователя"""
        pass

    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 100) -> List[UserEntity]:
        """Получить список пользователей"""
        pass


class RoleRepository(ABC):
    """Интерфейс репозитория для ролей"""

    @abstractmethod
    async def get_by_user(self, user_id: UUID) -> List[Role]:
        """Получить все роли пользователя"""
        pass

    @abstractmethod
    async def add(self, role: Role) -> None:
        """Добавить роль"""
        pass

    @abstractmethod
    async def remove(self, user_id: UUID, role_type: RoleType, branch_id: Optional[UUID] = None) -> None:
        """Удалить роль"""
        pass

    @abstractmethod
    async def get_users_by_role(self, role_type: RoleType, branch_id: Optional[UUID] = None) -> List[UUID]:
        """Получить ID пользователей с указанной ролью"""
        pass


class UnitOfWork(ABC):
    """
    Интерфейс Unit of Work для транзакций.
    
    Позволяет выполнять несколько операций в одной транзакции.
    """
    
    @abstractmethod
    async def __aenter__(self):
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    @abstractmethod
    async def commit(self):
        """Зафиксировать транзакцию"""
        pass

    @abstractmethod
    async def rollback(self):
        """Откатить транзакцию"""
        pass

    @property
    @abstractmethod
    def users(self) -> UserEntityRepository:
        """Репозиторий пользователей в рамках транзакции"""
        pass

    @property
    @abstractmethod
    def roles(self) -> RoleRepository:
        """Репозиторий ролей в рамках транзакции"""
        pass