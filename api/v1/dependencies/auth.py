from typing import Annotated, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from uuid import UUID

from domain.entities.user import UserEntity
from domain.entities.role import RoleType
from application.exceptions import UserNotFoundError, InvalidTokenError
from api.v1.dependencies.containers import get_container, Container

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    container: Annotated[Container, Depends(get_container)]
) -> UserEntity:
    """Получить текущего пользователя по токену"""
    # Проверяем токен
    payload = container.token_service.verify_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный или истекший токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = UUID(payload['sub'])
    
    # Пробуем получить из кэша
    user = await container.cache_service.get_user(user_id)
    if user:
        return user
    
    # Если нет в кэше, идем в БД
    async with container.get_uow() as uow:
        user = await uow.users.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не найден",
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Пользователь деактивирован",
            )
        
        # Загружаем роли
        roles = await uow.roles.get_by_user(user_id)
        for role in roles:
            user._roles.add(role)
        
        # Кэшируем
        await container.cache_service.set_user(user)
        
        return user


async def get_current_active_user(
    current_user: Annotated[UserEntity, Depends(get_current_user)]
) -> UserEntity:
    """Получить текущего активного пользователя"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь деактивирован"
        )
    return current_user


class RoleChecker:
    """Проверка наличия роли у пользователя"""
    
    def __init__(self, required_role: RoleType):
        self.required_role = required_role
    
    async def __call__(
        self,
        current_user: Annotated[UserEntity, Depends(get_current_active_user)]
    ) -> UserEntity:
        if not current_user.has_role(self.required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Требуется роль {self.required_role.value}"
            )
        return current_user


class BranchRoleChecker:
    """Проверка наличия роли в конкретном филиале"""
    
    def __init__(self, required_role: RoleType):
        self.required_role = required_role
    
    async def __call__(
        self,
        branch_id: UUID,
        current_user: Annotated[UserEntity, Depends(get_current_active_user)]
    ) -> UserEntity:
        if not current_user.has_role(self.required_role, branch_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Требуется роль {self.required_role.value} в филиале {branch_id}"
            )
        return current_user


# Готовые проверки ролей
require_admin = RoleChecker(RoleType.ADMIN)
require_super_admin = RoleChecker(RoleType.SUPER_ADMIN)
require_owner = RoleChecker(RoleType.OWNER)
require_manager = RoleChecker(RoleType.MANAGER)



from api.v1.dependencies.containers import get_container
from api.v1.mappers.auth import RegisterSchemaMapper
def get_register_mapper() -> RegisterSchemaMapper:
    return RegisterSchemaMapper()