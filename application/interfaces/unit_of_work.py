from abc import ABC, abstractmethod
from typing import Optional

from application.interfaces.repositories import (
    UserRepository, RoleRepository, BranchRepository
)


class UnitOfWork(ABC):
    """Интерфейс Unit of Work для транзакций"""
    
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
    def users(self) -> UserRepository:
        """Репозиторий пользователей"""
        pass
    
    @property
    @abstractmethod
    def roles(self) -> RoleRepository:
        """Репозиторий ролей"""
        pass
    
    @property
    @abstractmethod
    def branches(self) -> BranchRepository:
        """Репозиторий филиалов"""
        pass