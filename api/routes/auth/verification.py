from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status

from api.schemas.verification import (
    VerificationRequestSchema,
    VerificationResponseSchema
)
from api.dependencies.auth import (
    AuthUseCaseDependencies,
    AuthMappersDependencies,
)
from api.dependencies.security import get_current_user_id
from api.mappers.auth.verification import VerificationSchemaMapper

from application.use_cases.auth.verification import VerificationUseCase
from application.exceptions import (
    RateLimitExceededError,
    ValidationError
)


router = APIRouter()


@router.post(
    "/verification",
    response_model=VerificationResponseSchema,
    summary="Запрос кода верификации",
    responses={
        status.HTTP_200_OK: {"description": "Код успешно отправлен"},
        status.HTTP_400_BAD_REQUEST: {"description": "Некорректные данные"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Не авторизован"},
        status.HTTP_429_TOO_MANY_REQUESTS: {"description": "Превышен лимит запросов"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Внутренняя ошибка сервера"},
    }
)
async def request_verification_code(
    verification_data: VerificationRequestSchema,
    request: Request,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[VerificationUseCase, Depends(AuthUseCaseDependencies.verification)],
    mapper: Annotated[VerificationSchemaMapper, Depends(AuthMappersDependencies.verification)],
) -> VerificationResponseSchema:
    """
    Запрос кода верификации для подтверждения email или телефона.
    
    Отправляет код подтверждения на указанный email или телефон.
    
    **Параметры запроса:**
    - **email**: email для верификации (если не указан phone)
    - **phone**: номер телефона для верификации (если не указан email)
    
    **Возвращает:**
    - **success**: статус отправки
    - **message**: информационное сообщение
    - **expires_in**: время действия кода в секундах
    - **delivery_method**: способ доставки (email/sms)
    
    **Ограничения:**
    - Не более 3 запросов в час на один контакт
    - Код действителен в течение 10 минут
    """
    try:
        # Преобразование и выполнение
        dto = mapper.to_dto(
            verification_data, 
            current_user_id,
        )
        result = await use_case.execute(dto)
        
        return mapper.to_schema(result)
        
    except RateLimitExceededError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e) or "Превышен лимит запросов на отправку кода. Попробуйте позже."
        )
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e) or "Ошибка валидации данных"
        )
        
    except HTTPException:
        # Пробрасываем HTTP исключения дальше
        raise
        
    except Exception as e:
        # Логирование ошибки здесь
        # logger.error(f"Verification request error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Произошла внутренняя ошибка при запросе кода верификации"
        )