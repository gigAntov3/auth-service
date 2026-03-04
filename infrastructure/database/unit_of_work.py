from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from application.interfaces.unit_of_work import UnitOfWork

from infrastructure.database.repositories.user_repository import SQLAlchemyUserRepository
from infrastructure.database.repositories.role_repository import SQLAlchemyRoleRepository
from infrastructure.database.repositories.branch_repository import SQLAlchemyBranchRepository


class SQLAlchemyUnitOfWork(UnitOfWork):
    """Реализация Unit of Work на SQLAlchemy"""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory
        self.session: Optional[AsyncSession] = None

    async def __aenter__(self):
        self.session = self.session_factory()
        self._users = SQLAlchemyUserRepository(self.session)
        self._roles = SQLAlchemyRoleRepository(self.session)
        self._branches = SQLAlchemyBranchRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

    @property
    def users(self):
        return self._users

    @property
    def roles(self):
        return self._roles

    @property
    def branches(self):
        return self._branches