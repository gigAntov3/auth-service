from dataclasses import dataclass
from typing import Optional

from domain.entities.refresh_token import RefreshTokenEntity
from domain.interfaces.unit_of_work import UnitOfWork
from domain.interfaces.token_service import TokenService
# from domain.interfaces.password_hasher import PasswordHasher
from application.dtos.auth import LogoutRequestDTO
from application.exceptions import AuthenticationError, AccountNotActiveError

from config import settings

@dataclass
class LogoutUserUseCase:
    """Use case для входа пользователя"""
    
    uow: UnitOfWork
    # password_hasher: PasswordHasher
    token_service: TokenService
    
    async def execute(
        self,
        dto: LogoutRequestDTO,
    ) -> bool:
        async with self.uow:
            token = await self.uow.refresh_tokens.get_by_hash(dto.refresh_token)
            if not token:
                raise AuthenticationError("Invalid token")
            
            await self.uow.refresh_tokens.delete(dto.refresh_token)
            return True