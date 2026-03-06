from dataclasses import dataclass

from application.interfaces.unit_of_work import UnitOfWork
from application.interfaces.services.token_service import TokenService

from application.dtos.auth import LogoutRequestDTO
from application.exceptions import AuthenticationError


@dataclass
class LogoutUserUseCase:
    """Use case для входа пользователя"""
    
    uow: UnitOfWork
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