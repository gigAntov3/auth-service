from dataclasses import dataclass
from typing import Optional

from domain.entities.refresh_token import RefreshTokenEntity
from domain.interfaces.unit_of_work import UnitOfWork
from domain.interfaces.token_service import TokenService
from domain.interfaces.password_hasher import PasswordHasher
from application.dtos.auth import LoginRequestDTO, LoginResponseDTO
from application.exceptions import AuthenticationError, AccountNotActiveError

from config import settings

@dataclass
class LoginUserUseCase:
    """Use case для входа пользователя"""
    
    uow: UnitOfWork
    password_hasher: PasswordHasher
    token_service: TokenService
    
    async def execute(
        self,
        dto: LoginRequestDTO,
    ) -> LoginResponseDTO:
        async with self.uow:
            user = None
            if dto.email:
                user = await self.uow.users.get_by_email(dto.email)
            
            if not user:
                raise AuthenticationError("Invalid credentials")
            
            if not user.is_active:
                raise AccountNotActiveError("Account is deactivated")
            
            if not self.password_hasher.verify(dto.password, user.password_hash.value):
                raise AuthenticationError("Invalid credentials")
            
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
            
            return LoginResponseDTO(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=1800,
                user_id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email.value,
                role=user.role.type.value
            )