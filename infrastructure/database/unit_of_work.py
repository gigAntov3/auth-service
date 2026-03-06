from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from application.interfaces.unit_of_work import UnitOfWork
from infrastructure.database.repositories.users import SQLAlchemyUserRepository
from infrastructure.database.repositories.refresh_token import SQLAlchemyRefreshTokenRepository
from infrastructure.database.repositories.verification_code import SqlAlchemyVerificationCodeRepository

class SQLAlchemyUnitOfWork(UnitOfWork):
    """SQLAlchemy implementation of Unit of Work"""
    
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory
        self.session: Optional[AsyncSession] = None
    
    async def __aenter__(self):
        """Enter the context manager"""
        self.session = self.session_factory()
        
        # Initialize repositories
        self._users = SQLAlchemyUserRepository(self.session)
        self._refresh_tokens = SQLAlchemyRefreshTokenRepository(self.session)
        self._verification = SqlAlchemyVerificationCodeRepository(self.session)
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager"""
        if exc_type is not None:
            # An exception occurred, rollback
            await self.rollback()
        else:
            # No exception, commit
            await self.commit()
        
        await self.session.close()
        self.session = None
    
    async def commit(self):
        """Commit the current transaction"""
        await self.session.commit()
    
    async def rollback(self):
        """Rollback the current transaction"""
        await self.session.rollback()
    
    @property
    def users(self) -> SQLAlchemyUserRepository:
        return self._users
    
    @property
    def refresh_tokens(self) -> SQLAlchemyRefreshTokenRepository:
        return self._refresh_tokens
    
    @property
    def verification(self) -> SqlAlchemyVerificationCodeRepository:
        return self._verification
    

@asynccontextmanager
async def get_unit_of_work(
    session_factory: async_sessionmaker[AsyncSession]
) -> AsyncGenerator[SQLAlchemyUnitOfWork, None]:
    """Get a Unit of Work instance"""
    async with SQLAlchemyUnitOfWork(session_factory) as uow:
        yield uow