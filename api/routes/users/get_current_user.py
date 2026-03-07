from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated

from api.dependencies.users import UsersMappersDependencies
from api.dependencies.security import get_current_user
from api.mappers.users.getter import UserGetterSchemaMapper
from api.schemas.users import UserSchema


router = APIRouter(tags=["Users"])


@router.get(
    "/current",
    response_model=UserSchema,
    summary="Получение информации о текущем пользователе",
    responses={
        status.HTTP_200_OK: {"description": "Информация успешно получена"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Не авторизован"},
        status.HTTP_404_NOT_FOUND: {"description": "Пользователь не найден"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Внутренняя ошибка сервера"},
    }
)
async def get_current_user_info(
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    mapper: Annotated[UserGetterSchemaMapper, Depends(UsersMappersDependencies.getter)],
) -> UserSchema:
    """
    Получение информации о текущем аутентифицированном пользователе.
    
    Возвращает:
    - **id**: уникальный идентификатор пользователя
    - **email**: электронная почта
    - **first_name**: имя
    - **is_active**: статус аккаунта
    - **created_at**: дата регистрации
    - **updated_at**: дата последнего обновления
    """
    try:
        # Проверка наличия пользователя
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        
        # Маппинг и возврат результата
        return mapper.to_schema(current_user)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка валидации данных: {str(e)}"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Произошла внутренняя ошибка сервера при получении информации о пользователе"
        )