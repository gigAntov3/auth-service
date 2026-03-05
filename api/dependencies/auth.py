from typing import Optional, Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from infrastructure.security.jwt_service import JWTTokenService
from infrastructure.security.password_hasher import BcryptPasswordHasher
from infrastructure.services.email_service import MockEmailService
from infrastructure.services.sms_service import MockSMSService
from infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork
from infrastructure.database.session import db_manager
from application.exceptions import InvalidTokenError

from api.dependencies.base import (
    get_unit_of_work,
    get_email_service,
    get_sms_service,
)

from config import settings


def get_password_hasher():
    return BcryptPasswordHasher()

def get_token_service():
    return JWTTokenService(
        secret_key=settings.jwt.secret_key,
        algorithm=settings.jwt.algorithm,
        access_token_expire_minutes=settings.jwt.access_token_expire_minutes,
        refresh_token_expire_days=settings.jwt.refresh_token_expire_days
    )


from application.use_cases.auth.register_user import RegisterUserUseCase
from api.mappers.auth.register import RegisterSchemaMapper

def get_register_use_case(
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_unit_of_work)],
    password_hasher: Annotated[BcryptPasswordHasher, Depends(get_password_hasher)],
    token_service: Annotated[JWTTokenService, Depends(get_token_service)],
    email_service: Annotated[MockEmailService, Depends(get_email_service)],
) -> RegisterUserUseCase:
    return RegisterUserUseCase(
        uow=uow,
        password_hasher=password_hasher,
        token_service=token_service,
        email_service=email_service,
    )


def get_register_schema_mapper():
    return RegisterSchemaMapper()


from application.use_cases.auth.login_user import LoginUserUseCase
from api.mappers.auth.login import LoginSchemaMapper


def get_login_use_case(
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_unit_of_work)],
    password_hasher: Annotated[BcryptPasswordHasher, Depends(get_password_hasher)],
    token_service: Annotated[JWTTokenService, Depends(get_token_service)],
) -> LoginUserUseCase:
    return LoginUserUseCase(
        uow=uow,
        password_hasher=password_hasher,
        token_service=token_service,
    )


def get_login_schema_mapper():
    return LoginSchemaMapper()


from application.use_cases.auth.logout_user import LogoutUserUseCase
from api.mappers.auth.logout import LogoutSchemaMapper


def get_logout_use_case(
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_unit_of_work)],
    token_service: Annotated[JWTTokenService, Depends(get_token_service)],
) -> LogoutUserUseCase:
    return LogoutUserUseCase(
        uow=uow,
        token_service=token_service,
    )


def get_logout_schema_mapper():
    return LogoutSchemaMapper()


from application.use_cases.auth.refresh_user import RefreshUserUseCase
from api.mappers.auth.refresh import RefreshSchemaMapper


def get_refresh_use_case(
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_unit_of_work)],
    token_service: Annotated[JWTTokenService, Depends(get_token_service)],
) -> RefreshUserUseCase:
    return RefreshUserUseCase(
        uow=uow,
        token_service=token_service,
    )


def get_refresh_schema_mapper():
    return RefreshSchemaMapper()










from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated
from uuid import UUID

security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    token_service: Annotated[JWTTokenService, Depends(get_token_service)],
) -> UUID:

    token = credentials.credentials

    try:
        payload = token_service.verify_access_token(token)
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    return UUID(user_id)















# def require_permission(permission: str):
#     """Dependency для проверки прав доступа"""
#     async def permission_dependency(
#         current_user: Annotated[TokenData, Depends(get_current_user)]
#     ):
#         if permission not in current_user.permissions:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail=f"Permission required: {permission}"
#             )
#         return current_user
#     return permission_dependency