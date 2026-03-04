from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from domain.entities.user import UserEntity
from domain.entities.role import Role, RoleType
from domain.value_objects.email import Email
from domain.value_objects.password import PasswordHash

from application.interfaces.repositories import UserRepository

from infrastructure.database.models.user_model import UserModel
from infrastructure.database.models.role_model import RoleModel


class SQLAlchemyUserRepository(UserRepository):
    """Реализация репозитория пользователей на SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: UUID) -> Optional[UserEntity]:
        """Получить пользователя по ID"""
        result = await self.session.execute(
            select(UserModel)
            .where(UserModel.id == user_id)
            .options(selectinload(UserModel.roles))
        )
        model = result.scalar_one_or_none()
        return await self._to_domain(model) if model else None

    async def get_by_email(self, email: str) -> Optional[UserEntity]:
        """Получить пользователя по email"""
        result = await self.session.execute(
            select(UserModel)
            .where(UserModel.email == email)
            .options(selectinload(UserModel.roles))
        )
        model = result.scalar_one_or_none()
        return await self._to_domain(model) if model else None

    async def save(self, user: UserEntity) -> None:
        """Сохранить нового пользователя"""
        model = UserModel(
            id=user.id,
            email=user.email.value,
            full_name=user.full_name,
            password_hash=user.password_hash.value,
            is_active=user.is_active,
            is_email_verified=user.is_email_verified,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login_at=user.last_login_at
        )
        self.session.add(model)

    async def update(self, user: UserEntity) -> None:
        """Обновить пользователя"""
        await self.session.execute(
            update(UserModel)
            .where(UserModel.id == user.id)
            .values(
                full_name=user.full_name,
                password_hash=user.password_hash.value,
                is_active=user.is_active,
                is_email_verified=user.is_email_verified,
                updated_at=user.updated_at,
                last_login_at=user.last_login_at
            )
        )

    async def delete(self, user_id: UUID) -> None:
        """Удалить пользователя (hard delete)"""
        await self.session.execute(
            delete(UserModel).where(UserModel.id == user_id)
        )

    async def list(self, skip: int = 0, limit: int = 100, 
                   branch_id: Optional[UUID] = None) -> List[UserEntity]:
        """Получить список пользователей"""
        query = select(UserModel).options(selectinload(UserModel.roles))
        
        if branch_id:
            query = query.where(UserModel.home_branch_id == branch_id)
        
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        models = result.scalars().all()
        
        users = []
        for model in models:
            user = await self._to_domain(model)
            users.append(user)
        return users

    async def count(self, branch_id: Optional[UUID] = None) -> int:
        """Получить количество пользователей"""
        query = select(UserModel)
        if branch_id:
            query = query.where(UserModel.home_branch_id == branch_id)
        result = await self.session.execute(query)
        return len(result.scalars().all())

    async def _to_domain(self, model: UserModel) -> UserEntity:
        """Конвертировать модель в доменную сущность"""
        user = UserEntity(
            id=model.id,
            email=Email(model.email),
            full_name=model.full_name,
            password_hash=PasswordHash(model.password_hash),
            is_active=model.is_active,
            is_email_verified=model.is_email_verified,
            created_at=model.created_at,
            updated_at=model.updated_at,
            last_login_at=model.last_login_at
        )
        
        # Загружаем роли
        for role_model in model.roles:
            role = Role(
                id=role_model.id,
                user_id=role_model.user_id,
                role_type=RoleType(role_model.role_type),
                branch_id=role_model.branch_id,
                assigned_at=role_model.assigned_at,
                assigned_by=role_model.assigned_by
            )
            user._roles.add(role)
        
        return user