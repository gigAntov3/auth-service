from functools import lru_cache
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import redis.asyncio as redis

from infrastructure.config import settings
from infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork
from infrastructure.auth.password_hasher import BcryptPasswordHasher
from infrastructure.auth.jwt_service import JWTTokenService
from infrastructure.cache.redis_cache import RedisCacheService

if settings.ENVIRONMENT == "development" or settings.DEBUG:
    from infrastructure.email.dummy_sender import DummyEmailSender
    EmailSenderClass = DummyEmailSender
else:
    from infrastructure.email.smtp_sender import SMTPEmailSender
    EmailSenderClass = SMTPEmailSender

from application.use_cases.auth_use_cases import (
    RegisterUseCase,
    LoginUseCase,
    VerifyEmailUseCase,
    ForgotPasswordUseCase,
    ResetPasswordUseCase,
    RefreshTokenUseCase,
    ChangePasswordUseCase,
    LogoutUseCase
)


class Container:
    """DI контейнер для управления зависимостями"""
    
    def __init__(self):
        # Database
        self.engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DATABASE_ECHO,
            pool_size=settings.DATABASE_POOL_SIZE
        )
        self.session_factory = async_sessionmaker(self.engine, expire_on_commit=False)
        
        # Redis
        self.redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        
        # Services
        self.password_hasher = BcryptPasswordHasher()
        self.token_service = JWTTokenService()
        self.cache_service = RedisCacheService(self.redis_client)
        self.email_sender = EmailSenderClass()
    
    # Unit of Work
    def get_uow(self) -> SQLAlchemyUnitOfWork:
        return SQLAlchemyUnitOfWork(self.session_factory)
    
    # Use Cases
    def get_register_use_case(self) -> RegisterUseCase:
        return RegisterUseCase(
            uow=self.get_uow(),
            password_hasher=self.password_hasher,
            token_service=self.token_service,
            email_sender=self.email_sender,
            cache=self.cache_service
        )
    
    def get_login_use_case(self) -> LoginUseCase:
        return LoginUseCase(
            uow=self.get_uow(),
            password_hasher=self.password_hasher,
            token_service=self.token_service,
            cache=self.cache_service
        )
    
    def get_verify_email_use_case(self) -> VerifyEmailUseCase:
        return VerifyEmailUseCase(
            uow=self.get_uow(),
            token_service=self.token_service,
            cache=self.cache_service
        )
    
    def get_forgot_password_use_case(self) -> ForgotPasswordUseCase:
        return ForgotPasswordUseCase(
            uow=self.get_uow(),
            token_service=self.token_service,
            email_sender=self.email_sender,
            cache=self.cache_service
        )
    
    def get_reset_password_use_case(self) -> ResetPasswordUseCase:
        return ResetPasswordUseCase(
            uow=self.get_uow(),
            password_hasher=self.password_hasher,
            token_service=self.token_service,
            cache=self.cache_service
        )
    
    def get_refresh_token_use_case(self) -> RefreshTokenUseCase:
        return RefreshTokenUseCase(
            uow=self.get_uow(),
            token_service=self.token_service,
            cache=self.cache_service
        )
    
    def get_change_password_use_case(self) -> ChangePasswordUseCase:
        return ChangePasswordUseCase(
            uow=self.get_uow(),
            password_hasher=self.password_hasher,
            cache=self.cache_service
        )
    
    def get_logout_use_case(self) -> LogoutUseCase:
        return LogoutUseCase(cache=self.cache_service)


@lru_cache
def get_container() -> Container:
    """Синглтон для контейнера"""
    return Container()