from dataclasses import dataclass
from typing import Optional

from domain.entities.refresh_token import RefreshTokenEntity
from application.interfaces.unit_of_work import UnitOfWork
from application.interfaces.services.token_service import TokenService
# from domain.interfaces.password_hasher import PasswordHasher
from application.dtos.auth import RefreshRequestDTO, RefreshResponseDTO
from application.exceptions import AuthenticationError, AccountNotActiveError

from config import settings

@dataclass
class RefreshUserUseCase:
    """Use case для входа пользователя"""
    
    uow: UnitOfWork
    # password_hasher: PasswordHasher
    token_service: TokenService
    
    async def execute(
        self,
        dto: RefreshRequestDTO,
    ) -> RefreshResponseDTO:
        async with self.uow:
            refresh_token = await self.uow.refresh_tokens.get_by_hash(dto.refresh_token)
            if not refresh_token:
                raise AuthenticationError("Invalid token")
            
            if not refresh_token.is_valid():
                raise AuthenticationError("Invalid token")
            
            user = await self.uow.users.get_by_id(refresh_token.user_id)
            if not user:
                raise AuthenticationError("Invalid token")
            
            if not user.is_active:
                raise AccountNotActiveError("Account is deactivated")
            
            access_token = self.token_service.create_access_token(
                user_id=str(refresh_token.user_id),
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email.value,
                role=user.role.type.value
            )

            return RefreshResponseDTO(
                access_token=access_token,
                expires_in=settings.jwt.access_token_expire_minutes,
                refresh_token=refresh_token.token_hash,
            )