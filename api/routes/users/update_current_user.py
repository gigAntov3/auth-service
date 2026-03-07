from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from uuid import UUID

from api.dependencies.users import UsersUseCaseDependencies, UsersMappersDependencies
from api.dependencies.security import get_current_user_id
from api.mappers.users.update import UserUpdateSchemaMapper
from api.schemas.users import UserSchema, UserUpdateSchema
from application.use_cases.users.update_user import UpdateUserUseCase


router = APIRouter(tags=["Users"])


@router.post(
    "/current",
    response_model=UserSchema,
    summary="Обновление информации о текущем пользователе",
    responses={
        status.HTTP_200_OK: {"description": "Информация успешно обновлена"},
        status.HTTP_400_BAD_REQUEST: {"description": "Некорректные данные"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Не авторизован"},
        status.HTTP_404_NOT_FOUND: {"description": "Пользователь не найден"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Внутренняя ошибка сервера"},
    }
)
async def update_current_user(
    update: UserUpdateSchema,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[UpdateUserUseCase, Depends(UsersUseCaseDependencies.update)],
    mapper: Annotated[UserUpdateSchemaMapper, Depends(UsersMappersDependencies.update)],
) -> UserSchema:
    """
    Обновление информации о текущем пользователе
    
    - **email**: новый email пользователя (опционально)
    - **full_name**: новое полное имя (опционально)
    - **password**: новый пароль (опционально)
    """
    try:
        dto = mapper.to_dto(update, current_user_id)
        user_dto = await use_case.execute(dto)
        return mapper.to_schema(user_dto)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для выполнения операции"
        )
    except LookupError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Произошла внутренняя ошибка сервера"
        )