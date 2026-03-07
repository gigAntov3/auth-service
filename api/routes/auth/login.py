from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies.auth import (
    AuthMappersDependencies,
    AuthUseCaseDependencies,
)
from api.dependencies.base import get_device_info
from api.mappers.auth.login import LoginSchemaMapper
from api.schemas.auth import LoginRequestSchema, LoginResponseSchema

from application.dtos.auth import DeviceInfoDTO
from application.exceptions import (
    AccountNotActiveError,
    AuthenticationError,
    ValidationError,
    RateLimitExceededError,
)
from application.use_cases.auth.login_user import LoginUserUseCase


router = APIRouter()


@router.post(
    "/login",
    response_model=LoginResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Вход в систему",
    responses={
        status.HTTP_200_OK: {"description": "Успешный вход в систему"},
        status.HTTP_400_BAD_REQUEST: {"description": "Неверные данные для входа"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Неверные учетные данные или аккаунт не активен"},
        status.HTTP_429_TOO_MANY_REQUESTS: {"description": "Превышен лимит попыток входа"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Внутренняя ошибка сервера"},
    }
)
async def login(
    login_data: LoginRequestSchema,
    device_info: Annotated[DeviceInfoDTO, Depends(get_device_info)],
    use_case: Annotated[LoginUserUseCase, Depends(AuthUseCaseDependencies.login)],
    mapper: Annotated[LoginSchemaMapper, Depends(AuthMappersDependencies.login)],
) -> LoginResponseSchema:
    """
    Вход в систему.
    
    Ожидает:
    - **email** или **phone**: email или телефон пользователя
    - **password**: пароль пользователя
    - **remember_me**: запомнить сессию (опционально)
    
    Возвращает:
    - **access_token**: JWT токен доступа
    - **refresh_token**: JWT токен обновления
    - **token_type**: тип токена (Bearer)
    - **expires_in**: время жизни токена в секундах
    - **user_id**: ID пользователя
    
    Примечания:
    - Поддерживается вход по email или телефону
    - При неверных данных возвращается 401 Unauthorized
    - При превышении лимита попыток возвращается 429 Too Many Requests
    """
    try:
        # Преобразование и выполнение
        dto = mapper.to_dto(login_data, device_info)
        result = await use_case.execute(dto)
        
        return mapper.to_schema(result)
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e) or "Неверный email/телефон или пароль"
        )
        
    except AccountNotActiveError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e) or "Аккаунт не активирован. Пожалуйста, подтвердите email или телефон"
        )
        
    except RateLimitExceededError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e) or "Превышен лимит попыток входа. Попробуйте позже."
        )
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e) or "Неверный формат данных для входа"
        )
        
    except Exception as e:
        # Логирование ошибки здесь
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Произошла внутренняя ошибка при входе в систему"
        )