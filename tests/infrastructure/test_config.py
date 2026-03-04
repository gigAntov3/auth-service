import pytest
import os
from unittest.mock import patch


def test_settings_default_values():
    """Проверка значений по умолчанию"""
    # Создаем настройки с тестовыми значениями
    from infrastructure.config import Settings
    settings = Settings(
        JWT_SECRET_KEY="test_key",
        SMTP_HOST="test.com",
        SMTP_USERNAME="test",
        SMTP_PASSWORD="test",
        SMTP_FROM_EMAIL="test@test.com"
    )
    
    assert settings.DATABASE_POOL_SIZE == 20
    assert settings.JWT_ALGORITHM == "HS256"
    assert settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES == 30
    assert settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS == 7
    assert settings.SMTP_PORT == 587
    assert settings.SMTP_USE_TLS is True


def test_settings_can_be_overridden_by_env(monkeypatch):
    """Проверка, что настройки можно переопределить через переменные окружения"""
    monkeypatch.setenv("JWT_SECRET_KEY", "test_secret_key")
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost/test_db")
    monkeypatch.setenv("SMTP_HOST", "smtp.test.com")
    monkeypatch.setenv("SMTP_USERNAME", "test@test.com")
    monkeypatch.setenv("SMTP_PASSWORD", "password")
    monkeypatch.setenv("SMTP_FROM_EMAIL", "noreply@test.com")
    
    # Перезагружаем настройки
    from importlib import reload
    import infrastructure.config
    reload(infrastructure.config)
    from infrastructure.config import settings
    
    assert settings.JWT_SECRET_KEY == "test_secret_key"
    assert settings.DATABASE_URL == "postgresql://test:test@localhost/test_db"
    assert settings.SMTP_HOST == "smtp.test.com"