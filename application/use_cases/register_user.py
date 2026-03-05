from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from domain.entities.user import UserEntity
from domain.entities.refresh_token import RefreshTokenEntity


from domain.value_objects.role import Role
from application.interfaces.password_hasher import PasswordHasher
from application.interfaces.unit_of_work import UnitOfWork
from application.interfaces.services.token_service import TokenService
from application.dtos.auth import RegisterRequestDTO, RegisterResponseDTO
from application.interfaces.services.email_service import EmailService
from application.interfaces.services.sms_service import SmsService
from application.exceptions import UserAlreadyExistsError, ValidationError

from config import settings

@dataclass
class RegisterUserUseCase:
    """Use case для регистрации нового пользователя"""
    
    uow: UnitOfWork
    password_hasher: PasswordHasher
    token_service: TokenService
    email_service: EmailService
    
    async def execute(self, dto: RegisterRequestDTO) -> RegisterResponseDTO:
        async with self.uow:
            if dto.email:
                existing_user = await self.uow.users.get_by_email(dto.email)
                if existing_user:
                    raise UserAlreadyExistsError(f"User with email {dto.email} already exists")
            
            password_hash = self.password_hasher.hash(dto.password) if dto.password else None
            
            # Создание пользователя (доменная сущность)
            user = UserEntity.create(
                first_name=dto.first_name,
                last_name=dto.last_name,
                email=dto.email,
                password_hash=password_hash
            )
            
            # Сохранение пользователя
            await self.uow.users.save(user)
            
            # Создание токенов
            access_token = self.token_service.create_access_token(
                user_id=str(user.id),
                # email=user.email.value,
                # first_name=user.first_name,
                # last_name=user.last_name
            )
            
            refresh_token = self.token_service.create_refresh_token(
                user_id=str(user.id)
            )
            
            refresh_token_entity = RefreshTokenEntity.create(
                user_id=user.id,
                token_hash=refresh_token,
                expires_in_days=settings.jwt.refresh_token_expire_days,
                ip_address=dto.ip_address,
                user_agent=dto.user_agent
            )
            
            await self.uow.refresh_tokens.save(
                token=refresh_token_entity
            )
            
            await self.uow.commit()

            return RegisterResponseDTO(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=1800,
                user_id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email.value,
                role=user.role.type.value
            )