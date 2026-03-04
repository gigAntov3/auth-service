from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete

from domain.entities.role import Role, RoleType

from application.interfaces.repositories import RoleRepository

from infrastructure.database.models.role_model import RoleModel


class SQLAlchemyRoleRepository(RoleRepository):
    """Реализация репозитория ролей на SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, role_id: UUID) -> Optional[Role]:
        """Получить роль по ID"""
        result = await self.session.execute(
            select(RoleModel).where(RoleModel.id == role_id)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_by_user(self, user_id: UUID) -> List[Role]:
        """Получить все роли пользователя"""
        result = await self.session.execute(
            select(RoleModel).where(RoleModel.user_id == user_id)
        )
        models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    async def add(self, role: Role) -> None:
        """Добавить роль"""
        model = RoleModel(
            id=role.id,
            user_id=role.user_id,
            role_type=role.role_type.value,
            branch_id=role.branch_id,
            assigned_at=role.assigned_at,
            assigned_by=role.assigned_by
        )
        self.session.add(model)

    async def remove(self, user_id: UUID, role_type: RoleType, 
                     branch_id: Optional[UUID] = None) -> None:
        """Удалить роль"""
        query = delete(RoleModel).where(
            and_(
                RoleModel.user_id == user_id,
                RoleModel.role_type == role_type.value
            )
        )
        if branch_id:
            query = query.where(RoleModel.branch_id == branch_id)
        await self.session.execute(query)

    async def get_users_by_role(self, role_type: RoleType, 
                                 branch_id: Optional[UUID] = None) -> List[UUID]:
        """Получить ID пользователей с указанной ролью"""
        query = select(RoleModel.user_id).where(RoleModel.role_type == role_type.value)
        if branch_id:
            query = query.where(RoleModel.branch_id == branch_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def user_has_role(self, user_id: UUID, role_type: RoleType,
                            branch_id: Optional[UUID] = None) -> bool:
        """Проверить наличие роли у пользователя"""
        query = select(RoleModel).where(
            and_(
                RoleModel.user_id == user_id,
                RoleModel.role_type == role_type.value
            )
        )
        if branch_id:
            query = query.where(RoleModel.branch_id == branch_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    def _to_domain(self, model: RoleModel) -> Role:
        """Конвертировать модель в доменную сущность"""
        return Role(
            id=model.id,
            user_id=model.user_id,
            role_type=RoleType(model.role_type),
            branch_id=model.branch_id,
            assigned_at=model.assigned_at,
            assigned_by=model.assigned_by
        )