from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies.auth import (
    AuthMappersDependencies,
    AuthUseCaseDependencies,
)
from api.dependencies.base import get_device_info
from api.dependencies.security import get_current_user_id
from api.mappers.auth.register import RegisterSchemaMapper
from api.schemas.auth import RegisterRequestSchema
from api.schemas.auth import RegisterResponseSchema

from application.dtos.auth import DeviceInfoDTO
from application.exceptions import (
    UserAlreadyExistsError,
    ValidationError,
)
from application.use_cases.auth.register_user import RegisterUserUseCase


router = APIRouter()


@router.post(
    "/register",
    response_model=RegisterResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация пользователя",
    responses={
        status.HTTP_201_CREATED: {"description": "Пользователь успешно зарегистрирован"},
        status.HTTP_400_BAD_REQUEST: {"description": "Неверные данные для регистрации"},
        status.HTTP_409_CONFLICT: {"description": "Пользователь уже существует"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Внутренняя ошибка сервера"},
    }
)
async def register(
    register_request: RegisterRequestSchema,
    device_info: Annotated[DeviceInfoDTO, Depends(get_device_info)],
    use_case: Annotated[RegisterUserUseCase, Depends(AuthUseCaseDependencies.register)],
    mapper: Annotated[RegisterSchemaMapper, Depends(AuthMappersDependencies.register)],
) -> RegisterResponseSchema:
    """
    Регистрация нового пользователя.
    
    Ожидает:
    - **email**: email пользователя
    - **password**: пароль пользователя
    - **first_name**: имя пользователя (опционально)
    - **last_name**: фамилия пользователя (опционально)
    
    Возвращает:
    - **access_token**: JWT токен доступа
    - **refresh_token**: JWT токен обновления
    - **token_type**: тип токена (Bearer)
    - **expires_in**: время жизни токена в секундах
    """
    try:
        # Преобразование и выполнение
        dto = mapper.to_dto(register_request, device_info)
        result = await use_case.execute(dto)
        
        return mapper.to_schema(result)
        
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e) or "Пользователь с таким email уже существует"
        )
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e) or "Неверные данные для регистрации"
        )
        
    except Exception as e:
        # Логирование ошибки здесь
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Произошла внутренняя ошибка при регистрации пользователя"
        )