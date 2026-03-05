from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

from pydantic import ValidationError

logger = logging.getLogger(__name__)

def setup_exception_handlers(app: FastAPI):
    """Настройка обработчиков исключений"""
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Обработка HTTP исключений"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.status_code,
                    "message": exc.detail,
                    "path": request.url.path
                }
            }
        )
    
    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError):
        """Обработка ошибок валидации"""
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": 422,
                    "message": "Validation error",
                    "details": exc.errors,
                    "path": request.url.path
                }
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Обработка всех остальных исключений"""
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": 500,
                    "message": "Internal server error",
                    "path": request.url.path
                }
            }
        )