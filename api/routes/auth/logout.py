from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies.auth import (
    AuthMappersDependencies,
    AuthUseCaseDependencies,
)
from api.dependencies.base import get_device_info
from api.dependencies.security import get_refresh_token
from api.mappers.auth.logout import LogoutSchemaMapper
from api.schemas import MessageResponseSchema

from application.dtos.auth import DeviceInfoDTO
from application.exceptions import (
    AuthenticationError,
    InvalidTokenError,
    ValidationError,
)
from application.use_cases.auth.logout_user import LogoutUserUseCase


router = APIRouter()


@router.post(
    "/logout",
    response_model=MessageResponseSchema,
    summary="Выход из системы",
    responses={
        status.HTTP_200_OK: {"description": "Успешный выход из системы"},
        status.HTTP_400_BAD_REQUEST: {"description": "Неверный запрос или отсутствует refresh токен"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Недействительный refresh токен"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Внутренняя ошибка сервера"},
    }
)
async def logout(
    refresh_token: Annotated[str, Depends(get_refresh_token)],
    device_info: Annotated[DeviceInfoDTO, Depends(get_device_info)],
    use_case: Annotated[LogoutUserUseCase, Depends(AuthUseCaseDependencies.logout)],
    mapper: Annotated[LogoutSchemaMapper, Depends(AuthMappersDependencies.logout)],
) -> MessageResponseSchema:
    """
    Выход из системы (инвалидация refresh токенов).
    
    Ожидает:
    - **refresh_token**: Refresh токен для инвалидации (передается в заголовке Authorization или cookie)
    
    Возвращает:
    - **success**: Статус операции (true/false)
    - **message**: Информационное сообщение о результате
    """
    try:
        # Преобразование и выполнение
        dto = mapper.to_dto(refresh_token, device_info)
        await use_case.execute(dto)
        
        return MessageResponseSchema(
            success=True, 
            message="Выход из системы выполнен успешно"
        )
        
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e) or "Недействительный refresh токен"
        )
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e) or "Ошибка аутентификации при выходе из системы"
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
            detail="Произошла внутренняя ошибка при выходе из системы"
        )