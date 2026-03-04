"""
Infrastructure Layer - реализации интерфейсов из application слоя.

Содержит:
- Database: модели SQLAlchemy, репозитории, Unit of Work
- Auth: JWT сервис, хеширование паролей
- Cache: Redis кэш
- Email: SMTP отправка писем
- Config: настройки приложения
"""

from infrastructure.config import settings
from infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork
from infrastructure.auth.password_hasher import BcryptPasswordHasher
from infrastructure.auth.jwt_service import JWTTokenService
from infrastructure.cache.redis_cache import RedisCacheService
from infrastructure.email.smtp_sender import SMTPEmailSender

__all__ = [
    'settings',
    'SQLAlchemyUnitOfWork',
    'BcryptPasswordHasher',
    'JWTTokenService',
    'RedisCacheService',
    'SMTPEmailSender',
]