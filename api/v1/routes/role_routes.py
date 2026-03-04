from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Annotated, List, Optional
from uuid import UUID

from api.v1.dependencies.containers import get_container, Container
from api.v1.dependencies.auth import get_current_active_user, require_admin

from application.dtos.role_dto import (
    RoleAssignmentDTO,
    RoleDTO,
    RoleRemovalDTO,
    RoleTypeDTO
)
from application.dtos.user_dto import UserDTO

from application.exceptions import (
    UserNotFoundError,
    InsufficientPermissionsError,
    RoleAssignmentError
)

from domain.entities.user import UserEntity
from domain.entities.role import RoleType
from domain.services.authorization import AuthorizationService

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.post(
    "/assign",
    status_code=status.HTTP_201_CREATED,
    summary="Назначение роли пользователю"
)
async def assign_role(
    request: RoleAssignmentDTO,
    current_user: Annotated[UserEntity, Depends(get_current_active_user)],
    container: Annotated[Container, Depends(get_container)]
):
    """
    Назначение роли пользователю.
    
    Правила:
    - SUPER_ADMIN может назначать любые роли
    - ADMIN может назначать любые роли, кроме SUPER_ADMIN
    - OWNER может назначать бизнес-роли в своих филиалах
    """
    async with container.get_uow() as uow:
        # Получаем целевого пользователя
        target_user = await uow.users.get_by_id(request.user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        
        # Получаем его роли
        roles = await uow.roles.get_by_user(request.user_id)
        for role in roles:
            target_user._roles.add(role)
        
        # Проверяем права на назначение
        try:
            AuthorizationService.validate_role_assignment(
                current_user,
                target_user,
                RoleType(request.role_type.value),
                request.branch_id
            )
        except InsufficientPermissionsError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        except RoleAssignmentError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        
        # Создаем роль
        from domain.entities.role import Role
        role = Role.create(
            user_id=request.user_id,
            role_type=RoleType(request.role_type.value),
            assigned_by=current_user.id,
            branch_id=request.branch_id
        )
        
        # Сохраняем
        await uow.roles.add(role)
        await uow.commit()
        
        # Инвалидируем кэш пользователя
        await container.cache_service.delete_user(request.user_id)
    
    return {"message": "Роль успешно назначена"}


@router.delete(
    "/remove",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление роли у пользователя"
)
async def remove_role(
    request: RoleRemovalDTO,
    current_user: Annotated[UserEntity, Depends(get_current_active_user)],
    container: Annotated[Container, Depends(get_container)]
):
    """
    Удаление роли у пользователя.
    
    Требует те же права, что и назначение.
    """
    async with container.get_uow() as uow:
        # Получаем целевого пользователя
        target_user = await uow.users.get_by_id(request.user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        
        # Получаем его роли
        roles = await uow.roles.get_by_user(request.user_id)
        for role in roles:
            target_user._roles.add(role)
        
        # Проверяем права на удаление
        try:
            AuthorizationService.validate_role_assignment(
                current_user,
                target_user,
                RoleType(request.role_type.value),
                request.branch_id
            )
        except InsufficientPermissionsError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        except RoleAssignmentError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        
        # Нельзя удалить базовую роль USER
        if request.role_type.value == RoleTypeDTO.USER and not request.branch_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя удалить базовую роль USER"
            )
        
        # Удаляем роль
        await uow.roles.remove(
            request.user_id,
            RoleType(request.role_type.value),
            request.branch_id
        )
        await uow.commit()
        
        # Инвалидируем кэш пользователя
        await container.cache_service.delete_user(request.user_id)


@router.get(
    "/users/{role_type}",
    response_model=List[UserDTO],
    summary="Получение пользователей по роли"
)
async def get_users_by_role(
    role_type: RoleTypeDTO,  # path parameter - без default
    current_user: Annotated[UserEntity, Depends(require_admin)],  # dependency - без default
    container: Annotated[Container, Depends(get_container)],  # dependency - без default
    branch_id: Optional[UUID] = Query(None, description="Фильтр по филиалу")  # query parameter - с default
):
    """
    Получение списка пользователей с указанной ролью.
    
    Требует роль ADMIN или SUPER_ADMIN.
    """
    async with container.get_uow() as uow:
        user_ids = await uow.roles.get_users_by_role(
            RoleType(role_type.value),
            branch_id
        )
        
        users = []
        for user_id in user_ids:
            user = await uow.users.get_by_id(user_id)
            if user:
                roles = await uow.roles.get_by_user(user_id)
                users.append(UserDTO(
                    id=user.id,
                    email=user.email.value,
                    full_name=user.full_name,
                    is_active=user.is_active,
                    is_email_verified=user.is_email_verified,
                    created_at=user.created_at,
                    updated_at=user.updated_at,
                    last_login_at=user.last_login_at,
                    roles=[
                        RoleDTO(
                            id=role.id,
                            user_id=role.user_id,
                            role_type=role.role_type.value,
                            branch_id=role.branch_id,
                            assigned_at=role.assigned_at,
                            assigned_by=role.assigned_by
                        )
                        for role in roles
                    ]
                ))
        
        return users


@router.get(
    "/types",
    response_model=List[str],
    summary="Список всех типов ролей"
)
async def get_role_types(
    current_user: Annotated[UserEntity, Depends(get_current_active_user)]
):
    """Получение списка всех доступных типов ролей"""
    return [role.value for role in RoleType]