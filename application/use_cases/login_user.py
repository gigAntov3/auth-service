from dataclasses import dataclass
from typing import Optional

from domain.services.auth_service import AuthDomainService
from domain.interfaces.unit_of_work import UnitOfWork
from domain.interfaces.token_service import TokenService
from application.dtos.auth_dto import LoginDTO, TokenResponseDTO
from application.exceptions import AuthenticationError, AccountNotActiveError

@dataclass
class LoginUserUseCase:
    """Use case для входа пользователя"""
    
    uow: UnitOfWork
    auth_service: AuthDomainService
    token_service: TokenService
    
    async def execute(
        self,
        dto: LoginDTO,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> TokenResponseDTO:
        async with self.uow:
            # Поиск пользователя по email или телефону
            user = None
            if dto.email:
                user = await self.uow.users.get_by_email(dto.email)
            elif dto.phone:
                user = await self.uow.users.get_by_phone(dto.phone)
            
            if not user:
                raise AuthenticationError("Invalid credentials")
            
            # Проверка активности аккаунта
            if not user.is_active:
                raise AccountNotActiveError("Account is deactivated")
            
            # Аутентификация через доменный сервис
            is_authenticated = self.auth_service.authenticate(
                user=user,
                credentials=dto
            )
            
            if not is_authenticated:
                raise AuthenticationError("Invalid credentials")
            
            # Получение текущей компании и роли
            # В реальном приложении здесь может быть логика выбора компании
            memberships = await self.uow.memberships.get_by_user(user.id)
            active_membership = next(
                (m for m in memberships if m.is_active),
                None
            )
            
            # Создание токенов через доменный сервис
            access_token, refresh_token = self.auth_service.create_auth_tokens(
                user=user,
                company_id=str(active_membership.company_id) if active_membership else None,
                role=active_membership.role if active_membership else None,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Сохранение refresh токена
            await self.uow.refresh_tokens.save(refresh_token)
            await self.uow.commit()
            
            return TokenResponseDTO(
                access_token=access_token,
                refresh_token=refresh_token.token_hash,
                expires_in=1800,
                user_id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                role=active_membership.role.type.value if active_membership else None
            )