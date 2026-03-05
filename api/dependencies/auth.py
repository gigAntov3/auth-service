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

def get_email_service():
    return MockEmailService()

def get_sms_service():
    return MockSMSService()

def get_unit_of_work():
    return SQLAlchemyUnitOfWork(db_manager.session_factory)


from application.use_cases.register_user import RegisterUserUseCase
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


from application.use_cases.login_user import LoginUserUseCase
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


from application.use_cases.logout_user import LogoutUserUseCase
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


from application.use_cases.refresh_user import RefreshUserUseCase
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











# --- Auth / Security ---

security = HTTPBearer()

class TokenData(BaseModel):
    """Данные из токена"""
    user_id: UUID
    company_id: Optional[UUID] = None
    role: Optional[str] = None
    permissions: list[str] = []


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    token_service: JWTTokenService = Depends(get_token_service)
) -> TokenData:
    """Dependency для получения текущего пользователя из JWT"""
    token = credentials.credentials

    try:
        payload = token_service.verify_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        return TokenData(
            user_id=UUID(user_id),
            company_id=UUID(payload["company_id"]) if payload.get("company_id") else None,
            role=payload.get("role"),
            permissions=payload.get("permissions", [])
        )

    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_permission(permission: str):
    """Dependency для проверки прав доступа"""
    async def permission_dependency(
        current_user: Annotated[TokenData, Depends(get_current_user)]
    ):
        if permission not in current_user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission required: {permission}"
            )
        return current_user
    return permission_dependency