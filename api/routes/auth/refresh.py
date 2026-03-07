from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies.auth import (
    AuthMappersDependencies,
    AuthUseCaseDependencies,
)
from api.dependencies.base import get_device_info
from api.dependencies.security import get_refresh_token
from api.mappers.auth.refresh import RefreshSchemaMapper
from api.schemas.auth import RefreshResponseSchema

from application.dtos.auth import DeviceInfoDTO
from application.exceptions import (
    AuthenticationError,
    InvalidTokenError,
    ValidationError,
)
from application.use_cases.auth.refresh_user import RefreshUserUseCase


router = APIRouter()


@router.post(
    "/refresh",
    response_model=RefreshResponseSchema,
    summary="Обновление токена доступа",
    responses={
        status.HTTP_200_OK: {"description": "Токен успешно обновлен"},
        status.HTTP_400_BAD_REQUEST: {"description": "Неверный запрос или отсутствует refresh токен"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Недействительный или просроченный refresh токен"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Внутренняя ошибка сервера"},
    }
)
async def refresh_token(
    refresh_token: Annotated[str, Depends(get_refresh_token)],
    device_info: Annotated[DeviceInfoDTO, Depends(get_device_info)],
    use_case: Annotated[RefreshUserUseCase, Depends(AuthUseCaseDependencies.refresh)],
    mapper: Annotated[RefreshSchemaMapper, Depends(AuthMappersDependencies.refresh)],
) -> RefreshResponseSchema:
    """
    Обновление access токена с использованием refresh токена.
    
    Ожидает:
    - **refresh_token**: Действительный refresh токен (передается в заголовке Authorization или cookie)
    
    Возвращает:
    - **access_token**: Новый JWT токен доступа
    - **refresh_token**: Новый JWT токен обновления (если используется ротация)
    - **token_type**: Тип токена (Bearer)
    - **expires_in**: Время жизни нового токена в секундах
    """
    try:
        # Преобразование и выполнение
        dto = mapper.to_dto(refresh_token, device_info)
        result = await use_case.execute(dto)
        
        return mapper.to_schema(result)
        
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e) or "Недействительный или просроченный refresh токен"
        )
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e) or "Ошибка аутентификации при обновлении токена"
        )
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e) or "Неверный формат refresh токена"
        )
        
    except Exception as e:
        # Логирование ошибки здесь
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Произошла внутренняя ошибка при обновлении токена"
        )