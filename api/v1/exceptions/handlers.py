from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette import status
import logging
from typing import Union

from application.exceptions import (
    ApplicationError,
    AuthenticationError,
    AuthorizationError,
    UserNotFoundError,
    UserAlreadyExistsError,
    InvalidCredentialsError,
    InvalidTokenError,
    ValidationError
)

logger = logging.getLogger("api")


async def application_error_handler(
    request: Request,
    exc: Union[ApplicationError, Exception]
) -> JSONResponse:
    """Обработчик всех исключений приложения"""
    
    if isinstance(exc, ValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": str(exc)}
        )
    
    if isinstance(exc, UserNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)}
        )
    
    if isinstance(exc, UserAlreadyExistsError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)}
        )
    
    if isinstance(exc, (AuthenticationError, InvalidCredentialsError, InvalidTokenError)):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": str(exc)},
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if isinstance(exc, AuthorizationError):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": str(exc)}
        )
    
    # Логируем необработанные исключения
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Внутренняя ошибка сервера"}
    )


async def http_exception_handler(
    request: Request,
    exc: HTTPException
) -> JSONResponse:
    """Обработчик HTTP исключений FastAPI"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )