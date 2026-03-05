from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from api.dependencies.auth import (
    get_logout_schema_mapper,
    get_logout_use_case,
)
from api.mappers.auth.logout import LogoutSchemaMapper
from api.schemas.auth.logout import LogoutRequestSchema
from api.schemas import MessageResponseSchema

from application.use_cases.auth.logout_user import LogoutUserUseCase


router = APIRouter(prefix="/logout", tags=["Auth"])


@router.post(
    "",
    summary="Выход из системы"
)
async def logout(
    logout_request: LogoutRequestSchema,
    request: Request,
    use_case: Annotated[LogoutUserUseCase, Depends(get_logout_use_case)],
    mapper: Annotated[LogoutSchemaMapper, Depends(get_logout_schema_mapper)],
):
    """
    Выход из системы (инвалидация refresh токенов).
    """
    try:
        ip_address = request.client.host
        user_agent = request.headers.get("user-agent")

        dto = mapper.to_dto(logout_request, ip_address, user_agent)
        await use_case.execute(dto)
        return MessageResponseSchema(message="Logout successful")
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )