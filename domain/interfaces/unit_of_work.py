from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from domain.repositories.users import UserRepository
from domain.repositories.refresh_tokens import RefreshTokenRepository


class UnitOfWork(ABC):
    """Интерфейс Unit of Work для управления транзакциями"""
    
    @abstractmethod
    async def __aenter__(self):
        pass
    
    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    
    @abstractmethod
    async def commit(self):
        """Фиксация транзакции"""
        pass
    
    @abstractmethod
    async def rollback(self):
        """Откат транзакции"""
        pass
    
    @property
    @abstractmethod
    def users(self) -> UserRepository:
        """Получить репозиторий пользователей"""
        pass
    
    @property
    @abstractmethod
    def refresh_tokens(self) -> RefreshTokenRepository:
        """Получить репозиторий токенов обновления"""
        pass