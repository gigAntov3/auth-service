from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from api.dependencies.auth import (
    get_login_schema_mapper,
    get_login_use_case,
)
from api.mappers.auth.login import LoginSchemaMapper
from api.schemas.auth.login import LoginRequestSchema, LoginResponseSchema

from application.exceptions import (
    AccountNotActiveError,
    AuthenticationError,
)
from application.use_cases.login_user import LoginUserUseCase


router = APIRouter(prefix="/login", tags=["Auth"])


@router.post(
    "",
    response_model=LoginResponseSchema,
    status_code=status.HTTP_200_OK
)
async def login(
    login_request: LoginRequestSchema,
    request: Request,
    use_case: Annotated[LoginUserUseCase, Depends(get_login_use_case)],
    mapper: Annotated[LoginSchemaMapper, Depends(get_login_schema_mapper)],
) -> LoginResponseSchema:
    """
    Вход в систему.
    
    - Поддерживается вход по email или телефону
    - Возвращает access и refresh токены
    """
    try:
        ip_address = request.client.host
        user_agent = request.headers.get("user-agent")

        dto = mapper.to_dto(login_request, ip_address, user_agent)
        result = await use_case.execute(dto)
        return mapper.to_schema(result)
        
    except (AuthenticationError, AccountNotActiveError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )