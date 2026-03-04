from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from application.interfaces.repositories import BranchRepository

from infrastructure.database.models.branch_model import BranchModel


class SQLAlchemyBranchRepository(BranchRepository):
    """Реализация репозитория филиалов на SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, branch_id: UUID) -> Optional[BranchModel]:
        """Получить филиал по ID"""
        result = await self.session.execute(
            select(BranchModel).where(BranchModel.id == branch_id)
        )
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 100) -> List[BranchModel]:
        """Получить список филиалов"""
        result = await self.session.execute(
            select(BranchModel).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def get_by_ids(self, branch_ids: List[UUID]) -> List[BranchModel]:
        """Получить филиалы по списку ID"""
        result = await self.session.execute(
            select(BranchModel).where(BranchModel.id.in_(branch_ids))
        )
        return result.scalars().all()