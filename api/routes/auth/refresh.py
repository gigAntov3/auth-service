from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from api.dependencies.auth import (
    get_refresh_schema_mapper,
    get_refresh_use_case,
)
from api.mappers.auth.refresh import RefreshSchemaMapper
from api.schemas.auth.refresh import RefreshRequestSchema, RefreshResponseSchema

from application.exceptions import (
    AuthenticationError,
    InvalidTokenError,
)
from application.use_cases.auth.refresh_user import RefreshUserUseCase


router = APIRouter(prefix="/refresh", tags=["Auth"])


@router.post(
    "",
    response_model=RefreshResponseSchema,
    summary="Обновление токена доступа"
)
async def refresh_token(
    refresh_request: RefreshRequestSchema,
    request: Request,
    use_case: Annotated[RefreshUserUseCase, Depends(get_refresh_use_case)],
    mapper: Annotated[RefreshSchemaMapper, Depends(get_refresh_schema_mapper)],
) -> RefreshResponseSchema:
    """
    Обновление access токена с использованием refresh токена.
    """
    try:
        ip_address = request.client.host
        user_agent = request.headers.get("user-agent")

        dto = mapper.to_dto(refresh_request, ip_address, user_agent)
        result = await use_case.execute(dto)
        return mapper.to_schema(result)
        
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )