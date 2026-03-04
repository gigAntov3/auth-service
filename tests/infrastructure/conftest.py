import pytest
from infrastructure.config import Settings


@pytest.fixture(scope="session")
def test_settings():
    """Фикстура с настройками для тестов"""
    return Settings(
        JWT_SECRET_KEY="test_secret_key",
        SMTP_HOST="smtp.test.com",
        SMTP_USERNAME="test@test.com",
        SMTP_PASSWORD="password",
        SMTP_FROM_EMAIL="noreply@test.com",
        DATABASE_URL="sqlite+aiosqlite:///:memory:"
    )