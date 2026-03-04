from fastapi import APIRouter, Depends, HTTPException, status, Response
from typing import Annotated

from api.v1.dependencies.containers import get_container, Container
from api.v1.dependencies.auth import get_current_active_user

from application.dtos.auth_dto import (
    RegisterRequestDTO,
    RegisterResponseDTO,
    LoginRequestDTO,
    LoginResponseDTO,
    VerifyEmailRequestDTO,
    VerifyEmailResponseDTO,
    ForgotPasswordRequestDTO,
    ForgotPasswordResponseDTO,
    ResetPasswordRequestDTO,
    ResetPasswordResponseDTO,
    ChangePasswordRequestDTO,
    ChangePasswordResponseDTO,
    RefreshTokenRequestDTO,
    RefreshTokenResponseDTO,
    LogoutResponseDTO
)

from application.exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    UserNotFoundError,
    InvalidTokenError,
    ValidationError,
    UserNotActiveError
)

from api.v1.mappers.auth import RegisterSchemaMapper

from api.v1.dependencies.auth import get_register_mapper

from api.v1.schemas.auth import (
    RegisterRequestSchema,
    RegisterResponseSchema,
)

from domain.entities.user import UserEntity

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=RegisterResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя"
)
async def register(
    request: RegisterRequestDTO,
    container: Annotated[Container, Depends(get_container)],
    mapper: Annotated[RegisterSchemaMapper, Depends(get_register_mapper)]
) -> RegisterResponseSchema:
    """
    Регистрация нового пользователя:
    
    - **email**: должен быть уникальным
    - **password**: минимум 8 символов, заглавные, цифры, спецсимволы
    - **first_name**: имя пользователя
    - **last_name**: фамилия
    """
    use_case = container.get_register_use_case()
    try:
        result = await use_case.execute(request)
        return mapper.to_response(result)
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.post(
    "/login",
    response_model=LoginResponseDTO,
    summary="Вход в систему"
)
async def login(
    request: LoginRequestDTO,
    response: Response,
    container: Annotated[Container, Depends(get_container)]
):
    """
    Вход в систему с email и паролем.
    
    Возвращает access и refresh токены.
    Refresh token также устанавливается в httpOnly cookie.
    """
    use_case = container.get_login_use_case()
    try:
        result = await use_case.execute(request)
        
        # Устанавливаем refresh token в httpOnly cookie
        response.set_cookie(
            key="refresh_token",
            value=result.tokens.refresh_token,
            httponly=True,
            secure=True,  # В продакшене должно быть True
            samesite="lax",
            max_age=result.tokens.refresh_expires_in
        )
        
        return result
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except UserNotActiveError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/verify-email",
    response_model=VerifyEmailResponseDTO,
    summary="Подтверждение email"
)
async def verify_email(
    request: VerifyEmailRequestDTO,
    container: Annotated[Container, Depends(get_container)]
):
    """Подтверждение email с помощью токена из письма"""
    use_case = container.get_verify_email_use_case()
    try:
        result = await use_case.execute(request)
        return result
    except InvalidTokenError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/forgot-password",
    response_model=ForgotPasswordResponseDTO,
    summary="Запрос на сброс пароля"
)
async def forgot_password(
    request: ForgotPasswordRequestDTO,
    container: Annotated[Container, Depends(get_container)]
):
    """Отправка письма для сброса пароля"""
    use_case = container.get_forgot_password_use_case()
    result = await use_case.execute(request)
    return result


@router.post(
    "/reset-password",
    response_model=ResetPasswordResponseDTO,
    summary="Сброс пароля"
)
async def reset_password(
    request: ResetPasswordRequestDTO,
    container: Annotated[Container, Depends(get_container)]
):
    """Сброс пароля с использованием токена из письма"""
    use_case = container.get_reset_password_use_case()
    try:
        result = await use_case.execute(request)
        return result
    except InvalidTokenError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.post(
    "/refresh",
    response_model=RefreshTokenResponseDTO,
    summary="Обновление access токена"
)
async def refresh_token(
    request: RefreshTokenRequestDTO,
    container: Annotated[Container, Depends(get_container)]
):
    """Получение нового access токена с помощью refresh токена"""
    use_case = container.get_refresh_token_use_case()
    try:
        result = await use_case.execute(request)
        return result
    except InvalidTokenError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/change-password",
    response_model=ChangePasswordResponseDTO,
    summary="Изменение пароля"
)
async def change_password(
    request: ChangePasswordRequestDTO,
    current_user: Annotated[UserEntity, Depends(get_current_active_user)],
    container: Annotated[Container, Depends(get_container)]
):
    """Изменение пароля для авторизованного пользователя"""
    use_case = container.get_change_password_use_case()
    try:
        result = await use_case.execute(current_user.id, request)
        return result
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/logout",
    response_model=LogoutResponseDTO,
    summary="Выход из системы"
)
async def logout(
    response: Response,
    current_user: Annotated[UserEntity, Depends(get_current_active_user)],
    container: Annotated[Container, Depends(get_container)]
):
    """Выход из системы (инвалидация refresh токена)"""
    use_case = container.get_logout_use_case()
    await use_case.execute(current_user.id)
    
    # Удаляем cookie
    response.delete_cookie("refresh_token")
    
    return LogoutResponseDTO(message="Успешный выход из системы")


@router.get(
    "/me",
    response_model=dict,
    summary="Информация о текущем пользователе"
)
async def get_me(
    current_user: Annotated[UserEntity, Depends(get_current_active_user)]
):
    """Получение информации о текущем пользователе"""
    return {
        "id": str(current_user.id),
        "email": current_user.email.value,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "is_email_verified": current_user.is_email_verified,
        "roles": [
            {
                "role_type": role.role_type.value,
                "branch_id": str(role.branch_id) if role.branch_id else None,
                "is_global": role.is_global
            }
            for role in current_user.roles
        ],
        "permissions": current_user.get_all_permissions()
    }