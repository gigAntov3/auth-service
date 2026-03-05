from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from application.interfaces.unit_of_work import UnitOfWork

from application.dtos.users import UserResponseDTO
from application.exceptions import AuthenticationError

from config import settings

@dataclass
class UserGetterUseCase:
    """Use case для входа пользователя"""
    
    uow: UnitOfWork
    
    async def execute(
        self,
        user_id: UUID,
    ) -> UserResponseDTO:
        async with self.uow:
            user = await self.uow.users.get_by_id(user_id)
            if not user:
                raise AuthenticationError("Invalid user_id")
            
            return UserResponseDTO(
                id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email.value,
                phone=user.phone.value if user.phone else None,
                role=user.role.type.value,
                is_email_verified=user.is_email_verified,
                is_phone_verified=user.is_phone_verified,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )