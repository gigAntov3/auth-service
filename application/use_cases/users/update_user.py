from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from domain.entities.user import UserEntity
from application.interfaces.unit_of_work import UnitOfWork

from application.dtos.users import (
    UserResponseDTO,
    UserUpdateDTO,
)
from application.exceptions import AuthenticationError, UserNotFoundError

from config import settings

@dataclass
class UpdateUserUseCase:
    """Use case для входа пользователя"""
    
    uow: UnitOfWork
    
    async def execute(
        self,
        dto: UserUpdateDTO,
    ) -> UserResponseDTO:
        async with self.uow:
            user = await self.uow.users.get_by_id(dto.user_id)
            if not user:
                raise UserNotFoundError(f"User with id {dto.user_id} not found")
            
            if dto.email is not None:
                user.change_email(dto.email)
            
            if dto.phone is not None:
                user.change_phone(dto.phone)

            if any([dto.first_name, dto.last_name, dto.birthday, dto.gender]):
                user.update_profile(
                    first_name=dto.first_name,
                    last_name=dto.last_name,
                    birthday=dto.birthday,
                    gender=dto.gender
                )

            updated_user = await self.uow.users.save(user)

            await self.uow.commit()
            
            return UserResponseDTO(
                user_id=updated_user.id,
                first_name=updated_user.first_name,
                last_name=updated_user.last_name,
                email=updated_user.email.value,
                phone=updated_user.phone.value if updated_user.phone else None,
                birthday=updated_user.birthday,
                gender=updated_user.gender,
                role=updated_user.role.type.value,
                is_email_verified=updated_user.is_email_verified,
                is_phone_verified=updated_user.is_phone_verified,
                is_active=updated_user.is_active,
                created_at=updated_user.created_at,
                updated_at=updated_user.updated_at,
            )