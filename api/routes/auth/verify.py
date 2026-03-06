from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from api.schemas.verification import (
    VerifyRequestSchema,
    VerifyResponseSchema
)
from api.dependencies.auth import (
    get_verify_use_case,
    get_verify_schema_mapper,
)
from api.mappers.auth.verify import VerifySchemaMapper

from application.use_cases.auth.verify import VerifyUseCase
from application.exceptions import (
    RateLimitExceededError,
    ValidationError
)

router = APIRouter(prefix="/verify", tags=["Auth"])


@router.post(
    "", 
    response_model=VerifyResponseSchema
)
async def verify(
    verify: VerifyRequestSchema,
    use_case: Annotated[VerifyUseCase, Depends(get_verify_use_case)],
    mapper: Annotated[VerifySchemaMapper, Depends(get_verify_schema_mapper)],
) -> VerifyResponseSchema:
    """Проверка кода верификации"""
    try:
        dto = mapper.to_dto(verify)
        result = await use_case.execute(dto)
        return mapper.to_schema(result)
    except (RateLimitExceededError, ValidationError) as e:
        raise HTTPException(status_code=429 if isinstance(e, RateLimitExceededError) else 400, detail=str(e))