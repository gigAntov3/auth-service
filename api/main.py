from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from infrastructure.config import settings
from infrastructure.database.base import Base

from api.v1.routes import router as v1_router
from api.v1.middlewares.logging import LoggingMiddleware, MetricsMiddleware
from api.v1.exceptions.handlers import application_error_handler, http_exception_handler

from application.exceptions import ApplicationError

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения
    """
    logger.info("Starting up application...")
    
    # Создаем таблицы в БД (только для разработки)
    if settings.DEBUG:
        from sqlalchemy.ext.asyncio import create_async_engine
        
        engine = create_async_engine(settings.DATABASE_URL)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        await engine.dispose()
        logger.info("Database tables created")
    
    yield
    
    logger.info("Shutting down application...")
    
    # Закрываем соединения
    from api.v1.dependencies.containers import get_container
    container = get_container()
    await container.redis_client.close()
    await container.engine.dispose()


def create_app() -> FastAPI:
    """Фабрика приложения"""
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Auth Service API",
        docs_url="/api/docs" if settings.DEBUG else None,
        redoc_url="/api/redoc" if settings.DEBUG else None,
        lifespan=lifespan
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.DEBUG else ["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Custom middlewares
    app.add_middleware(LoggingMiddleware)
    if not settings.DEBUG:
        app.add_middleware(MetricsMiddleware)
    
    # Exception handlers
    app.add_exception_handler(ApplicationError, application_error_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    
    # Routes
    api_v1_prefix = "/api/v1"
    
    app.include_router(
        router=v1_router,
        prefix=api_v1_prefix
    )
    
    return app


app = create_app()