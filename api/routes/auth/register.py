from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from api.dependencies.auth import (
    get_register_schema_mapper,
    get_register_use_case,
)
from api.mappers.auth.register import RegisterSchemaMapper
from api.schemas.auth.register import RegisterRequestSchema, RegisterResponseSchema

from application.exceptions import (
    UserAlreadyExistsError,
    ValidationError,
)
from application.use_cases.auth.register_user import RegisterUserUseCase


router = APIRouter(prefix="/register", tags=["Auth"])


@router.post(
    "",
    response_model=RegisterResponseSchema,
    status_code=status.HTTP_201_CREATED
)
async def register(
    register_request: RegisterRequestSchema,
    request: Request,
    use_case: Annotated[RegisterUserUseCase, Depends(get_register_use_case)],
    mapper: Annotated[RegisterSchemaMapper, Depends(get_register_schema_mapper)]
) -> RegisterResponseSchema:
    try:
        ip_address = request.client.host
        user_agent = request.headers.get("user-agent")

        dto = mapper.to_dto(register_request, ip_address, user_agent)
        result = await use_case.execute(dto)
        return mapper.to_schema(result)
        
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )