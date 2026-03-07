from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request

from api.schemas.verification import (
    VerificationRequestSchema,
    VerificationResponseSchema
)
from api.dependencies.auth import (
    get_verification_use_case,
    get_verification_schema_mapper,
    get_current_user_id,
)
from api.mappers.auth.verification import VerificationSchemaMapper

from application.use_cases.auth.verification import RequestVerificationUseCase
from application.exceptions import (
    RateLimitExceededError,
    ValidationError
)

router = APIRouter(prefix="/verification", tags=["Auth"])


@router.post(
    "", 
    response_model=VerificationResponseSchema,
    summary="Запрос кода верификации"
)
async def request_verification(
    verification: VerificationRequestSchema,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[RequestVerificationUseCase, Depends(get_verification_use_case)],
    mapper: Annotated[VerificationSchemaMapper, Depends(get_verification_schema_mapper)],
) -> VerificationResponseSchema:
    """Запрос кода верификации"""
    try:
        dto = mapper.to_dto(verification, current_user_id)
        result = await use_case.execute(dto)
        return mapper.to_schema(result)
    except (RateLimitExceededError, ValidationError) as e:
        raise HTTPException(status_code=429 if isinstance(e, RateLimitExceededError) else 400, detail=str(e))