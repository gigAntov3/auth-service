from typing import Optional, List
from uuid import UUID
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from domain.entities.user import UserEntity
from domain.repositories.users import UserRepository
from infrastructure.database.models.user import UserModel
from infrastructure.database.mappers.users import UserMapper

from infrastructure.database.exceptions import UserAlreadyExistsError

class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy implementation of UserRepository"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.mapper = UserMapper()
    
    async def save(self, user: UserEntity) -> None:
        """Save or update user"""
        # Check if user exists
        existing = await self.get_by_id(user.id)
        
        if existing:
            # Update existing
            user_model = await self.session.get(UserModel, user.id)
            if user_model:
                user_model.email = user.email.value
                user_model.phone = user.phone
                user_model.password_hash = user.password_hash.value
                user_model.first_name = user.first_name
                user_model.last_name = user.last_name
                user_model.role = user.role.type.value
                user_model.is_email_verified = user.is_email_verified
                user_model.is_phone_verified = user.is_phone_verified
                user_model.is_active = user.is_active
                user_model.updated_at = user.updated_at
        else:
            # Create new
            user_model = self.mapper.to_model(user)
            self.session.add(user_model)
        
        try:
            await self.session.flush()
        except IntegrityError as e:
            raise UserAlreadyExistsError("User with this email or phone already exists") from e
    
    async def get_by_id(self, user_id: UUID) -> Optional[UserEntity]:
        """Get user by ID"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        user_model = result.scalar_one_or_none()
        return self.mapper.to_entity(user_model) if user_model else None
    
    async def get_by_email(self, email: str) -> Optional[UserEntity]:
        """Get user by email"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        user_model = result.scalar_one_or_none()
        return self.mapper.to_entity(user_model) if user_model else None
    
    async def get_by_phone(self, phone: str) -> Optional[UserEntity]:
        """Get user by phone"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.phone == phone)
        )
        user_model = result.scalar_one_or_none()
        return self.mapper.to_entity(user_model) if user_model else None
    
    async def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email"""
        result = await self.session.execute(
            select(UserModel.id).where(UserModel.email == email).limit(1)
        )
        return result.first() is not None
    
    async def exists_by_phone(self, phone: str) -> bool:
        """Check if user exists by phone"""
        result = await self.session.execute(
            select(UserModel.id).where(UserModel.phone == phone).limit(1)
        )
        return result.first() is not None
    
    async def update_last_login(self, user_id: UUID) -> None:
        """Update user's last login timestamp"""
        await self.session.execute(
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(updated_at=datetime.utcnow())
        )