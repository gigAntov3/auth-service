from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from infrastructure.security.jwt_service import JWTTokenService
from infrastructure.security.password_hasher import BcryptPasswordHasher
from application.exceptions import InvalidTokenError

from api.dependencies.users import UsersUseCaseDependencies

from application.use_cases.users.get_user_by_id import UserGetterUseCase
from application.dtos.users import UserResponseDTO

from config import settings


security = HTTPBearer()


def get_password_hasher() -> BcryptPasswordHasher:
    return BcryptPasswordHasher()

def get_token_service() -> JWTTokenService:
    return JWTTokenService(
        secret_key=settings.jwt.secret_key,
        algorithm=settings.jwt.algorithm,
        access_token_expire_minutes=settings.jwt.access_token_expire_minutes,
        refresh_token_expire_days=settings.jwt.refresh_token_expire_days
    )


async def get_current_user_id(
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


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    token_service: Annotated[JWTTokenService, Depends(get_token_service)],
    use_case: Annotated[UserGetterUseCase, Depends(UsersUseCaseDependencies.getter)],
) -> UserResponseDTO:
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
    
    return await use_case.execute(UUID(user_id))


async def get_refresh_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    token_service: Annotated[JWTTokenService, Depends(get_token_service)],
) -> str:
    token = credentials.credentials

    try:
        token_service.verify_refresh_token(token)
        return token
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )