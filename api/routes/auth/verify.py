from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from api.schemas.verification import VerifyRequestSchema, VerifyResponseSchema
from api.dependencies.auth import AuthUseCaseDependencies, AuthMappersDependencies
from api.dependencies.security import get_current_user_id
from api.mappers.auth.verify import VerifySchemaMapper

from application.use_cases.auth.verify import VerifyUseCase
from application.exceptions import RateLimitExceededError, ValidationError


router = APIRouter()


@router.post(
    "/verify",
    response_model=VerifyResponseSchema,
    summary="Проверка кода верификации",
    responses={
        status.HTTP_200_OK: {"description": "Код успешно проверен"},
        status.HTTP_400_BAD_REQUEST: {"description": "Неверный код или данные"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Не авторизован"},
        status.HTTP_429_TOO_MANY_REQUESTS: {"description": "Превышен лимит попыток"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Внутренняя ошибка сервера"},
    }
)
async def verify_code(
    verify_data: VerifyRequestSchema,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[VerifyUseCase, Depends(AuthUseCaseDependencies.verify)],
    mapper: Annotated[VerifySchemaMapper, Depends(AuthMappersDependencies.verify)],
) -> VerifyResponseSchema:
    """
    Проверка кода верификации для подтверждения email или телефона.
    
    Ожидает:
    - **email** или **phone**: контакт для верификации
    - **code**: 6-значный код подтверждения
    
    Возвращает:
    - **success**: статус верификации
    - **message**: информационное сообщение
    - **verified_at**: время подтверждения (если успешно)
    """
    try:
        # Преобразование и выполнение
        dto = mapper.to_dto(verify_data, current_user_id)
        result = await use_case.execute(dto)
        
        return mapper.to_schema(result)
        
    except RateLimitExceededError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e) or "Превышен лимит попыток ввода кода. Попробуйте позже."
        )
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e) or "Неверный код верификации"
        )

        
    except Exception as e:
        # Логирование ошибки здесь
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Произошла внутренняя ошибка при проверке кода"
        )