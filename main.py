import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

from api import router as api_router
from api.middlewares.rate_limit import RateLimitMiddleware

from config import settings
from infrastructure.database.session import db_manager


# # Настройка логирования
# logging.basicConfig(
#     level=logging.INFO if not settings.environment.debug else logging.DEBUG,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan контекст для управления ресурсами"""

    await db_manager.initialize()
    
    yield

    await db_manager.close()


app = FastAPI(
    title="Auth Service API",
    description="Multi-tenant authentication service",
    version="1.0.0",
    lifespan=lifespan,
    # docs_url="/docs" if settings.environment.debug else None,
    docs_url="/docs",
    redoc_url="/redoc" if settings.environment.debug else None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.origins,
    allow_credentials=settings.cors.allow_credentials,
    allow_methods=settings.cors.allow_methods,
    allow_headers=settings.cors.allow_headers,
    expose_headers=settings.cors.expose_headers,
    max_age=settings.cors.max_age
)

# Custom middlewares
app.add_middleware(RateLimitMiddleware)

# Подключение роутов
app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )