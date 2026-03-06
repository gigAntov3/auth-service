from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from uuid import UUID

from api.dependencies.auth import get_current_user_id
from api.dependencies.users import (
    get_user_update_use_case,
    get_user_update_schema_mapper,
)

from api.mappers.users.update import UserUpdateSchemaMapper
from api.schemas.users import (
    UserSchema,
    UserUpdateSchema,
)

from application.dtos.users import UserResponseDTO
from application.use_cases.users.update_user import UpdateUserUseCase


router = APIRouter()


@router.post(
    "/current",
    response_model=UserSchema,
    summary="Получение информации о текущем пользователе"
)
async def update_current_user(
    update: UserUpdateSchema,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[UpdateUserUseCase, Depends(get_user_update_use_case)],
    mapper: Annotated[UserUpdateSchemaMapper, Depends(get_user_update_schema_mapper)],
) -> UserSchema:
    """
    Получение информации о текущем аутентифицированном пользователе.
    """
    # try:
    print("\n\n\n\n")
    print(update)
    print("\n\n\n\n")
    dto = mapper.to_dto(update, current_user_id)
    current_user = await use_case.execute(dto)
    print(current_user)
    return mapper.to_schema(current_user)
        
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         detail=str(e)
    #     )