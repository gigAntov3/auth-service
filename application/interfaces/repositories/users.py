from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from domain.entities.user import UserEntity

class UserRepository(ABC):
    @abstractmethod
    async def save(self, user: UserEntity) -> None:
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[UserEntity]:
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[UserEntity]:
        pass
    
    @abstractmethod
    async def get_by_phone(self, phone: str) -> Optional[UserEntity]:
        pass
    
    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        pass
    
    @abstractmethod
    async def exists_by_phone(self, phone: str) -> bool:
        pass