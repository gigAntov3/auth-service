from abc import ABC, abstractmethod
from typing import Optional, List, Any
from uuid import UUID

from domain.entities.user import UserEntity
from domain.entities.role import Role, RoleType


class UserRepository(ABC):
    """Интерфейс репозитория пользователей"""
    
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[UserEntity]:
        """Получить пользователя по ID"""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[UserEntity]:
        """Получить пользователя по email"""
        pass
    
    @abstractmethod
    async def save(self, user: UserEntity) -> None:
        """Сохранить пользователя"""
        pass
    
    @abstractmethod
    async def update(self, user: UserEntity) -> None:
        """Обновить пользователя"""
        pass
    
    @abstractmethod
    async def delete(self, user_id: UUID) -> None:
        """Удалить пользователя"""
        pass
    
    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 100, 
                   branch_id: Optional[UUID] = None) -> List[UserEntity]:
        """Получить список пользователей"""
        pass
    
    @abstractmethod
    async def count(self, branch_id: Optional[UUID] = None) -> int:
        """Получить количество пользователей"""
        pass


class RoleRepository(ABC):
    """Интерфейс репозитория ролей"""
    
    @abstractmethod
    async def get_by_id(self, role_id: UUID) -> Optional[Role]:
        """Получить роль по ID"""
        pass
    
    @abstractmethod
    async def get_by_user(self, user_id: UUID) -> List[Role]:
        """Получить все роли пользователя"""
        pass
    
    @abstractmethod
    async def add(self, role: Role) -> None:
        """Добавить роль"""
        pass
    
    @abstractmethod
    async def remove(self, user_id: UUID, role_type: RoleType, 
                     branch_id: Optional[UUID] = None) -> None:
        """Удалить роль"""
        pass
    
    @abstractmethod
    async def get_users_by_role(self, role_type: RoleType, 
                                 branch_id: Optional[UUID] = None) -> List[UUID]:
        """Получить ID пользователей с указанной ролью"""
        pass
    
    @abstractmethod
    async def user_has_role(self, user_id: UUID, role_type: RoleType,
                            branch_id: Optional[UUID] = None) -> bool:
        """Проверить наличие роли у пользователя"""
        pass


class BranchRepository(ABC):
    """Интерфейс репозитория филиалов"""
    
    @abstractmethod
    async def get_by_id(self, branch_id: UUID) -> Optional[Any]:
        """Получить филиал по ID"""
        pass
    
    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 100) -> List[Any]:
        """Получить список филиалов"""
        pass
    
    @abstractmethod
    async def get_by_ids(self, branch_ids: List[UUID]) -> List[Any]:
        """Получить филиалы по списку ID"""
        pass