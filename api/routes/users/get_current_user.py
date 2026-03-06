from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated

from api.dependencies.auth import get_current_user
from api.dependencies.users import (
    get_user_getter_schema_mapper,
)

from api.mappers.users.getter import UserGetterSchemaMapper
from api.schemas.users import UserSchema

from application.use_cases.users.get_user_by_id import UserGetterUseCase


router = APIRouter()


@router.get(
    "/current",
    response_model=UserSchema,
    summary="Получение информации о текущем пользователе"
)
async def get_current_user(
    current_user: Annotated[int, Depends(get_current_user)],
    mapper: Annotated[UserGetterSchemaMapper, Depends(get_user_getter_schema_mapper)],
) -> UserSchema:
    """
    Получение информации о текущем аутентифицированном пользователе.
    """
    try:
        return mapper.to_schema(current_user)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )