from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated

from api.dependencies.auth import get_current_user
from api.dependencies.users import (
    get_user_getter_use_case,
    get_user_getter_schema_mapper,
)

from api.mappers.users.getter import UserGetterSchemaMapper
from api.schemas.users import GetUserResponseSchema

from application.use_cases.users.get_user_by_id import UserGetterUseCase


router = APIRouter(prefix="/current-user", tags=["Auth"])


@router.get(
    "",
    response_model=GetUserResponseSchema,
    summary="Получение информации о текущем пользователе"
)
async def get_current_user(
    current_user_id: Annotated[int, Depends(get_current_user)],
    use_case: Annotated[UserGetterUseCase, Depends(get_user_getter_use_case)],
    mapper: Annotated[UserGetterSchemaMapper, Depends(get_user_getter_schema_mapper)],
) -> GetUserResponseSchema:
    """
    Получение информации о текущем аутентифицированном пользователе.
    """
    try:
        current_user = await use_case.execute(current_user_id)
        return mapper.to_schema(current_user)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )