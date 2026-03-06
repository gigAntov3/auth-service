from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from api.dependencies.auth import (
    get_logout_schema_mapper,
    get_logout_use_case,
    get_refresh_token,
)
from api.dependencies.base import get_device_info

from api.mappers.auth.logout import LogoutSchemaMapper
from api.schemas import MessageResponseSchema

from application.dtos.auth import DeviceInfoDTO
from application.use_cases.auth.logout_user import LogoutUserUseCase


router = APIRouter(prefix="/logout", tags=["Auth"])


@router.post(
    "",
    summary="Выход из системы"
)
async def logout(
    request: Request,
    refresh_token: Annotated[str, Depends(get_refresh_token)],
    device_info: Annotated[DeviceInfoDTO, Depends(get_device_info)],
    use_case: Annotated[LogoutUserUseCase, Depends(get_logout_use_case)],
    mapper: Annotated[LogoutSchemaMapper, Depends(get_logout_schema_mapper)],
):
    """
    Выход из системы (инвалидация refresh токенов).
    """
    try:
        dto = mapper.to_dto(refresh_token, device_info)
        await use_case.execute(dto)
        return MessageResponseSchema(success=True, message="Logout successful")
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )