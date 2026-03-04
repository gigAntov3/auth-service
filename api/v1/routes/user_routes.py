from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Annotated, List, Optional
from uuid import UUID
from datetime import datetime, timezone

from api.v1.dependencies.containers import get_container, Container
from api.v1.dependencies.auth import get_current_active_user, require_admin

from application.dtos.user_dto import (
    UserDTO,
    UserCreateDTO,
    UserUpdateDTO,
    UserListDTO,
    UserPermissionsDTO
)
from application.dtos.role_dto import RoleDTO

from application.exceptions import (
    UserNotFoundError,
    UserAlreadyExistsError,
    ValidationError
)

from domain.entities.user import UserEntity
from domain.entities.role import RoleType

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/",
    response_model=UserListDTO,
    summary="Список пользователей"
)
async def get_users(
    current_user: Annotated[UserEntity, Depends(require_admin)],
    container: Annotated[Container, Depends(get_container)],
    skip: int = Query(0, ge=0, description="Сколько пропустить"),
    limit: int = Query(100, ge=1, le=1000, description="Сколько вернуть"),
    branch_id: Optional[UUID] = Query(None, description="Фильтр по филиалу")
):
    """
    Получение списка пользователей с пагинацией.
    
    Требует роль ADMIN или SUPER_ADMIN.
    """
    async with container.get_uow() as uow:
        users = await uow.users.list(skip=skip, limit=limit, branch_id=branch_id)
        total = await uow.users.count(branch_id=branch_id)
        
        # Конвертируем в DTO
        user_dtos = []
        for user in users:
            roles = await uow.roles.get_by_user(user.id)
            user_dtos.append(UserDTO(
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
        
        return UserListDTO(
            items=user_dtos,
            total=total,
            page=skip // limit + 1 if limit > 0 else 1,
            size=limit,
            pages=(total + limit - 1) // limit if limit > 0 else 1
        )


@router.post(
    "/",
    response_model=UserDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Создание пользователя"
)
async def create_user(
    request: UserCreateDTO,
    current_user: Annotated[UserEntity, Depends(require_admin)],
    container: Annotated[Container, Depends(get_container)]
):
    """
    Создание нового пользователя администратором.
    
    Требует роль ADMIN или SUPER_ADMIN.
    """
    # Проверяем, не занят ли email
    async with container.get_uow() as uow:
        existing = await uow.users.get_by_email(request.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует"
            )
    
    # Хешируем пароль
    password_hash = container.password_hasher.hash(request.password)
    
    # Создаем пользователя
    user = UserEntity.create(
        email=request.email,
        full_name=request.full_name,
        password_hash=password_hash
    )
    
    # Сохраняем
    async with container.get_uow() as uow:
        await uow.users.save(user)
        
        # Сохраняем базовую роль USER
        for role in user.roles:
            await uow.roles.add(role)
        
        await uow.commit()
    
    # Кэшируем
    await container.cache_service.set_user(user)
    
    return UserDTO(
        id=user.id,
        email=user.email.value,
        full_name=user.full_name,
        is_active=user.is_active,
        is_email_verified=user.is_email_verified,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login_at=user.last_login_at,
        roles=[]
    )


@router.get(
    "/{user_id}",
    response_model=UserDTO,
    summary="Получение пользователя по ID"
)
async def get_user(
    user_id: UUID,
    current_user: Annotated[UserEntity, Depends(get_current_active_user)],
    container: Annotated[Container, Depends(get_container)]
):
    """
    Получение информации о пользователе по ID.
    
    Доступно:
    - ADMIN и SUPER_ADMIN могут смотреть любого
    - Обычные пользователи только себя
    """
    # Проверяем права
    if current_user.id != user_id and not current_user.has_role(RoleType.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для просмотра этого пользователя"
        )
    
    async with container.get_uow() as uow:
        user = await uow.users.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        
        roles = await uow.roles.get_by_user(user_id)
    
    return UserDTO(
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
    )


@router.patch(
    "/{user_id}",
    response_model=UserDTO,
    summary="Обновление пользователя"
)
async def update_user(
    user_id: UUID,
    request: UserUpdateDTO,
    current_user: Annotated[UserEntity, Depends(get_current_active_user)],
    container: Annotated[Container, Depends(get_container)]
):
    """
    Обновление данных пользователя.
    
    Доступно:
    - ADMIN и SUPER_ADMIN могут обновлять любого
    - Обычные пользователи только себя
    """
    # Проверяем права
    if current_user.id != user_id and not current_user.has_role(RoleType.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для обновления этого пользователя"
        )
    
    async with container.get_uow() as uow:
        user = await uow.users.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        
        # Обновляем поля
        if request.full_name is not None:
            user.full_name = request.full_name
        if request.email is not None:
            # Проверяем, не занят ли новый email
            existing = await uow.users.get_by_email(request.email)
            if existing and existing.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email уже используется"
                )
            user.email = request.email
        if request.is_active is not None:
            user.is_active = request.is_active
        
        user.updated_at = datetime.now(timezone.utc)
        
        await uow.users.update(user)
        await uow.commit()
        
        # Обновляем кэш
        await container.cache_service.set_user(user)
        
        roles = await uow.roles.get_by_user(user_id)
    
    return UserDTO(
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
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление пользователя"
)
async def delete_user(
    user_id: UUID,
    current_user: Annotated[UserEntity, Depends(require_admin)],
    container: Annotated[Container, Depends(get_container)]
):
    """
    Удаление пользователя (hard delete).
    
    Требует роль ADMIN или SUPER_ADMIN.
    """
    async with container.get_uow() as uow:
        user = await uow.users.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        
        await uow.users.delete(user_id)
        await uow.commit()
        
        # Удаляем из кэша
        await container.cache_service.delete_user(user_id)
        await container.cache_service.delete_refresh_token(user_id)


@router.get(
    "/{user_id}/permissions",
    response_model=UserPermissionsDTO,
    summary="Получение разрешений пользователя"
)
async def get_user_permissions(
    user_id: UUID,
    current_user: Annotated[UserEntity, Depends(get_current_active_user)],
    container: Annotated[Container, Depends(get_container)]
):
    """
    Получение всех разрешений пользователя.
    
    Доступно:
    - ADMIN и SUPER_ADMIN могут смотреть любого
    - Обычные пользователи только себя
    """
    # Проверяем права
    if current_user.id != user_id and not current_user.has_role(RoleType.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )
    
    async with container.get_uow() as uow:
        user = await uow.users.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        
        roles = await uow.roles.get_by_user(user_id)
        for role in roles:
            user._roles.add(role)
    
    return UserPermissionsDTO(
        user_id=user.id,
        email=user.email.value,
        permissions=user.get_all_permissions()
    )