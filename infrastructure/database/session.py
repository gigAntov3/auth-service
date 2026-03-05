from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
    AsyncEngine
)
from sqlalchemy.pool import NullPool

from infrastructure.database.models.base import Base

from config import settings


class DatabaseManager:
    """Database connection manager"""
    
    def __init__(self, database_url: str, **kwargs):
        self.database_url = database_url
        self.engine: Optional[AsyncEngine] = None
        self.session_factory: Optional[async_sessionmaker[AsyncSession]] = None
        self.kwargs = kwargs
    
    async def initialize(self):
        """Initialize database connection"""
        
        # Проверяем, что это SQLite
        if not self.database_url.startswith('sqlite'):
            # Принудительно меняем на SQLite для разработки
            self.database_url = "sqlite+aiosqlite:///./auth_service.db"
            print(f"⚠️  Forcing SQLite database: {self.database_url}")
        
        # Настройки для SQLite
        connect_args = {"check_same_thread": False}
        
        # Create engine
        self.engine = create_async_engine(
            self.database_url,
            echo=settings.environment.debug,
            connect_args=connect_args,
            poolclass=NullPool,  # SQLite не поддерживает пулы соединений
            **self.kwargs
        )
        
        # Create session factory
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Создаем таблицы (для разработки)
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print("✅ Database tables created/verified")
        except Exception as e:
            print(f"⚠️  Error creating tables: {e}")
        
        print(f"✅ Database initialized: {self.database_url}")
    
    async def close(self):
        """Close database connection"""
        if self.engine:
            await self.engine.dispose()
            print("✅ Database connection closed")
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session"""
        if not self.session_factory:
            raise RuntimeError("Database not initialized")
        
        async with self.session_factory() as session:
            try:
                yield session
            finally:
                await session.close()


db_manager = DatabaseManager(settings.database.url)