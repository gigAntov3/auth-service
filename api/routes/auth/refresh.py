from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from api.dependencies.auth import (
    get_refresh_schema_mapper,
    get_refresh_use_case,
    get_refresh_token,
)
from api.dependencies.base import get_device_info
from api.mappers.auth.refresh import RefreshSchemaMapper
from api.schemas.auth import RefreshResponseSchema

from application.dtos.auth import DeviceInfoDTO
from application.exceptions import (
    AuthenticationError,
    InvalidTokenError,
)
from application.use_cases.auth.refresh_user import RefreshUserUseCase


router = APIRouter()


@router.post(
    "/refresh",
    response_model=RefreshResponseSchema,
    summary="Обновление токена доступа"
)
async def refresh_token(
    refresh_token: Annotated[str, Depends(get_refresh_token)],
    use_case: Annotated[RefreshUserUseCase, Depends(get_refresh_use_case)],
    mapper: Annotated[RefreshSchemaMapper, Depends(get_refresh_schema_mapper)],
) -> RefreshResponseSchema:
    """
    Обновление access токена с использованием refresh токена.
    """
    try:
        dto = mapper.to_dto(refresh_token)
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