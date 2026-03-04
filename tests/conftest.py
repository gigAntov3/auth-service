import pytest
from unittest.mock import AsyncMock, Mock
from uuid import uuid4, UUID

# Исправленные импорты
from domain.entities.user import UserEntity
from domain.entities.role import Role, RoleType
from domain.value_objects.email import Email
from domain.value_objects.password import PasswordHash

from tests.helpers import get_valid_password_hash


@pytest.fixture
def user_id() -> UUID:
    """Фикстура для ID пользователя"""
    return uuid4()


@pytest.fixture
def branch_id() -> UUID:
    """Фикстура для ID филиала"""
    return uuid4()


@pytest.fixture
def test_user(user_id: UUID) -> UserEntity:
    """Фикстура для тестового пользователя"""
    user = UserEntity(
        id=user_id,
        email=Email("test@example.com"),
        full_name="Test UserEntity",
        password_hash=PasswordHash(get_valid_password_hash()),
        is_active=True,
        is_email_verified=True
    )
    return user


@pytest.fixture
def mock_uow() -> Mock:
    """Фикстура для мока Unit of Work"""
    uow = AsyncMock()
    uow.users = AsyncMock()
    uow.roles = AsyncMock()
    uow.branches = AsyncMock()
    uow.commit = AsyncMock()
    uow.rollback = AsyncMock()
    
    # Настраиваем асинхронные методы
    uow.users.get_by_email = AsyncMock()
    uow.users.get_by_id = AsyncMock()
    uow.users.save = AsyncMock()
    uow.users.update = AsyncMock()
    uow.roles.get_by_user = AsyncMock()
    uow.roles.add = AsyncMock()
    
    return uow


@pytest.fixture
def mock_password_hasher() -> Mock:
    """Фикстура для мока PasswordHasher"""
    hasher = Mock()
    hasher.hash.return_value = "hashed_password"
    hasher.verify.return_value = True
    return hasher


@pytest.fixture
def mock_token_service() -> Mock:
    """Фикстура для мока TokenService"""
    service = Mock()
    service.create_access_token.return_value = ("access_token", 3600)
    service.create_refresh_token.return_value = ("refresh_token", 86400)
    service.create_email_verification_token.return_value = "verification_token"
    service.create_password_reset_token.return_value = "reset_token"
    service.verify_access_token.return_value = {"sub": str(uuid4()), "type": "access"}
    service.verify_refresh_token.return_value = {"sub": str(uuid4()), "type": "refresh"}
    service.verify_email_token.return_value = {
        "user_id": str(uuid4()),
        "email": "test@example.com",
        "type": "email_verification"
    }
    service.verify_password_reset_token.return_value = {
        "user_id": str(uuid4()),
        "email": "test@example.com",
        "type": "password_reset"
    }
    return service


@pytest.fixture
def mock_cache() -> AsyncMock:
    """Фикстура для мока CacheService"""
    cache = AsyncMock()
    cache.get_user = AsyncMock(return_value=None)
    cache.set_user = AsyncMock()
    cache.delete_user = AsyncMock()
    cache.get_refresh_token = AsyncMock(return_value="refresh_token")
    cache.set_refresh_token = AsyncMock()
    cache.delete_refresh_token = AsyncMock()
    cache.get_password_reset_token = AsyncMock(return_value="reset_token")
    cache.set_password_reset_token = AsyncMock()
    cache.delete_password_reset_token = AsyncMock()
    return cache


@pytest.fixture
def mock_email_sender() -> AsyncMock:
    """Фикстура для мока EmailSender"""
    sender = AsyncMock()
    sender.send_verification_email = AsyncMock()
    sender.send_password_reset_email = AsyncMock()
    sender.send_welcome_email = AsyncMock()
    return sender

import pytest
from unittest.mock import patch


@pytest.fixture(autouse=True)
def mock_settings():
    """Фикстура для мока настроек во всех тестах"""
    with patch('infrastructure.config.settings') as mock_settings:
        # JWT
        mock_settings.JWT_SECRET_KEY = "test_secret_key"
        mock_settings.JWT_ALGORITHM = "HS256"
        mock_settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
        mock_settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7
        mock_settings.JWT_EMAIL_VERIFY_EXPIRE_HOURS = 24
        mock_settings.JWT_PASSWORD_RESET_EXPIRE_HOURS = 1
        
        # Email
        mock_settings.SMTP_HOST = "smtp.test.com"
        mock_settings.SMTP_PORT = 587
        mock_settings.SMTP_USERNAME = "test@test.com"
        mock_settings.SMTP_PASSWORD = "password"
        mock_settings.SMTP_FROM_EMAIL = "noreply@test.com"
        mock_settings.SMTP_FROM_NAME = "Test Service"
        mock_settings.SMTP_USE_TLS = True
        
        # Frontend
        mock_settings.FRONTEND_URL = "http://localhost:3000"
        mock_settings.VERIFY_EMAIL_URL = "/verify-email"
        mock_settings.RESET_PASSWORD_URL = "/reset-password"
        
        # Database
        mock_settings.DATABASE_URL = "sqlite+aiosqlite:///:memory:"
        
        yield mock_settings