from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request

from api.schemas.auth.verification import (
    VerificationRequestSchema,
    VerificationRequestResponseSchema,
)
from api.dependencies.auth import (
    get_request_verification_use_case,
    get_request_verification_schema_mapper,
)
from api.mappers.auth.request_verification import VerificationRequestSchemaMapper

from application.use_cases.auth.request_verification import RequestVerificationUseCase
from application.exceptions import (
    RateLimitExceededError,
    ValidationError
)

router = APIRouter(prefix="/verification-request", tags=["Auth"])


@router.post(
    "", 
    response_model=VerificationRequestResponseSchema
)
async def request_verification(
    verification_request: VerificationRequestSchema,
    use_case: Annotated[RequestVerificationUseCase, Depends(get_request_verification_use_case)],
    mapper: Annotated[VerificationRequestSchemaMapper, Depends(get_request_verification_schema_mapper)],
) -> VerificationRequestResponseSchema:
    """Запрос кода верификации"""
    try:
        result = await use_case.execute(mapper.to_dto(verification_request))
        return mapper.to_schema(result)
    except (RateLimitExceededError, ValidationError) as e:
        raise HTTPException(status_code=429 if isinstance(e, RateLimitExceededError) else 400, detail=str(e))