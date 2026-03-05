from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Annotated

from api.schemas.auth import (
    RegisterRequestSchema, UserLoginRequest, TokenResponse,
    RefreshTokenRequest, UserResponse, VerifyEmailRequest,
    VerifyPhoneRequest, MessageResponse, RegisterResponseSchema
)
from api.dependencies.auth import get_current_user, TokenData, get_unit_of_work


from api.dependencies.auth import (
    get_register_use_case,
    get_register_schema_mapper,
)


from application.use_cases.register_user import RegisterUserUseCase
from application.use_cases.login_user import LoginUserUseCase
from application.exceptions import (
    UserAlreadyExistsError, AuthenticationError,
    AccountNotActiveError, InvalidTokenError, ValidationError
)

from infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork

from api.mappers.auth.register import RegisterSchemaMapper

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post(
    "/register",
    response_model=RegisterResponseSchema,
    status_code=status.HTTP_201_CREATED
)
async def register(
    request: RegisterRequestSchema,
    use_case: Annotated[RegisterUserUseCase, Depends(get_register_use_case)],
    mapper: Annotated[RegisterSchemaMapper, Depends(get_register_schema_mapper)]
) -> RegisterResponseSchema:
    try:
        dto = mapper.to_dto(request)
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

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Вход в систему"
)
async def login(
    request: Request,
    login_data: UserLoginRequest,
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_unit_of_work)]
):
    """
    Вход в систему.
    
    - Поддерживается вход по email или телефону
    - Возвращает access и refresh токены
    """
    try:
        use_case: LoginUserUseCase = request.app.state.login_user_use_case
        use_case.uow = uow
        
        # Получаем IP и User-Agent для аудита
        ip_address = request.client.host
        user_agent = request.headers.get("user-agent")
        
        result = await use_case.execute(
            dto=login_data,
            ip_address=ip_address,
            user_agent=user_agent
        )
        return result
        
    except (AuthenticationError, AccountNotActiveError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

















# @router.post(
#     "/refresh",
#     response_model=TokenResponse,
#     summary="Обновление токена доступа"
# )
# async def refresh_token(
#     request: Request,
#     refresh_data: RefreshTokenRequest,
#     uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_unit_of_work)]
# ):
#     """
#     Обновление access токена с использованием refresh токена.
#     """
#     try:
#         use_case: RefreshTokenUseCase = request.app.state.refresh_token_use_case
#         use_case.uow = uow
        
#         result = await use_case.execute(refresh_data.refresh_token)
#         return result
        
#     except InvalidTokenError as e:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail=str(e)
#         )

# @router.post(
#     "/verify-email",
#     response_model=MessageResponse,
#     summary="Верификация email"
# )
# async def verify_email(
#     request: Request,
#     verify_data: VerifyEmailRequest,
#     uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_unit_of_work)]
# ):
#     """
#     Подтверждение email с помощью кода верификации.
#     """
#     try:
#         use_case: VerifyEmailUseCase = request.app.state.verify_email_use_case
#         use_case.uow = uow
        
#         result = await use_case.execute(
#             email=verify_data.email,
#             code=verify_data.code
#         )
#         return result
        
#     except ValidationError as e:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=str(e)
#         )

# @router.post(
#     "/verify-phone",
#     response_model=MessageResponse,
#     summary="Верификация телефона"
# )
# async def verify_phone(
#     request: Request,
#     verify_data: VerifyPhoneRequest,
#     uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_unit_of_work)]
# ):
#     """
#     Подтверждение телефона с помощью кода верификации.
#     """
#     try:
#         use_case: VerifyPhoneUseCase = request.app.state.verify_phone_use_case
#         use_case.uow = uow
        
#         result = await use_case.execute(
#             phone=verify_data.phone,
#             code=verify_data.code
#         )
#         return result
        
#     except ValidationError as e:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=str(e)
#         )

# @router.post(
#     "/logout",
#     response_model=MessageResponse,
#     summary="Выход из системы"
# )
# async def logout(
#     request: Request,
#     current_user: Annotated[TokenData, Depends(get_current_user)],
#     uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_unit_of_work)]
# ):
#     """
#     Выход из системы (инвалидация refresh токенов).
#     """
#     try:
#         use_case: LogoutUserUseCase = request.app.state.logout_user_use_case
#         use_case.uow = uow
        
#         await use_case.execute(current_user.user_id)
#         return MessageResponse(message="Successfully logged out")
        
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=str(e)
#         )

# @router.get(
#     "/me",
#     response_model=UserResponse,
#     summary="Получение информации о текущем пользователе"
# )
# async def get_current_user_info(
#     request: Request,
#     current_user: Annotated[TokenData, Depends(get_current_user)],
#     uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_unit_of_work)]
# ):
#     """
#     Получение информации о текущем аутентифицированном пользователе.
#     """
#     try:
#         use_case: GetUserInfoUseCase = request.app.state.get_user_info_use_case
#         use_case.uow = uow
        
#         user = await use_case.execute(current_user.user_id)
#         return user
        
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=str(e)
#         )