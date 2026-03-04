from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    """Настройки приложения из environment variables"""
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"  # значение по умолчанию для тестов
    DATABASE_POOL_SIZE: int = 20
    DATABASE_ECHO: bool = False
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_POOL_SIZE: int = 10
    REDIS_DEFAULT_TTL: int = 3600
    
    # JWT
    JWT_SECRET_KEY: str = "test_secret_key_for_development"  # значение по умолчанию
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_EMAIL_VERIFY_EXPIRE_HOURS: int = 24
    JWT_PASSWORD_RESET_EXPIRE_HOURS: int = 1
    
    # Email
    SMTP_HOST: str = "localhost"  # значение по умолчанию
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = "test"  # значение по умолчанию
    SMTP_PASSWORD: str = "test"  # значение по умолчанию
    SMTP_FROM_EMAIL: str = "noreply@test.com"  # значение по умолчанию
    SMTP_FROM_NAME: str = "Auth Service"
    SMTP_USE_TLS: bool = True
    
    # App
    APP_NAME: str = "Auth Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # Frontend URLs
    FRONTEND_URL: str = "http://localhost:3000"
    VERIFY_EMAIL_URL: str = "/verify-email"
    RESET_PASSWORD_URL: str = "/reset-password"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # игнорировать лишние поля


settings = Settings()