import pytest
from uuid import uuid4
from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock

from application.exceptions import (
    UserEntityAlreadyExistsError,
    InvalidCredentialsError,
    UserEntityNotFoundError,
    InvalidTokenError,
    ValidationError
)

from application.use_cases.auth_use_cases import (
    RegisterUseCase,
    LoginUseCase,
    VerifyEmailUseCase,
    ForgotPasswordUseCase,
    ResetPasswordUseCase,
    ChangePasswordUseCase,
    RefreshTokenUseCase,
    LogoutUseCase
)
from application.dtos.auth_dto import (
    RegisterRequestDTO,
    LoginRequestDTO,
    VerifyEmailRequestDTO,
    ForgotPasswordRequestDTO,
    ResetPasswordRequestDTO,
    ChangePasswordRequestDTO,
    RefreshTokenRequestDTO
)

from domain.entities.user import UserEntity
from domain.entities.role import RoleType
from domain.value_objects.email import Email
from domain.value_objects.password import PasswordHash

from tests.helpers import get_valid_password_hash, TEST_PASSWORD


class TestRegisterUseCase:
    """Тесты для регистрации пользователя"""

    @pytest.mark.asyncio
    async def test_register_success(self):
        """Успешная регистрация"""
        # Arrange
        mock_uow = AsyncMock()
        mock_uow.users.get_by_email = AsyncMock(return_value=None)
        mock_uow.users.save = AsyncMock()
        mock_uow.roles.add = AsyncMock()
        mock_uow.commit = AsyncMock()

        mock_password_hasher = Mock()
        # ИСПРАВЛЕНО: используем реальный bcrypt хеш
        valid_hash = get_valid_password_hash("StrongP@ssw0rd")
        mock_password_hasher.hash.return_value = valid_hash

        mock_token_service = Mock()
        mock_token_service.create_email_verification_token.return_value = "verification_token"

        mock_email_sender = AsyncMock()
        mock_email_sender.send_verification_email = AsyncMock()

        mock_cache = AsyncMock()
        mock_cache.set_user = AsyncMock()

        use_case = RegisterUseCase(
            uow=mock_uow,
            password_hasher=mock_password_hasher,
            token_service=mock_token_service,
            email_sender=mock_email_sender,
            cache=mock_cache
        )

        request = RegisterRequestDTO(
            email="test@example.com",
            password="StrongP@ssw0rd",
            full_name="Test UserEntity"
        )

        # Act
        result = await use_case.execute(request)

        # Assert
        assert result.email == "test@example.com"
        assert result.full_name == "Test UserEntity"
        assert result.requires_verification is True

        mock_uow.users.get_by_email.assert_called_once_with("test@example.com")
        mock_uow.users.save.assert_called_once()
        mock_uow.roles.add.assert_called_once()
        mock_uow.commit.assert_called_once()
        mock_email_sender.send_verification_email.assert_called_once()
        mock_cache.set_user.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_user_already_exists(self):
        """Регистрация с существующим email"""
        # Arrange
        mock_uow = AsyncMock()
        existing_user = Mock(spec=UserEntity)
        mock_uow.users.get_by_email = AsyncMock(return_value=existing_user)

        use_case = RegisterUseCase(
            uow=mock_uow,
            password_hasher=Mock(),
            token_service=Mock(),
            email_sender=AsyncMock(),
            cache=AsyncMock()
        )

        request = RegisterRequestDTO(
            email="existing@example.com",
            password="StrongP@ssw0rd",
            full_name="Test UserEntity"
        )

        # Act & Assert
        with pytest.raises(UserEntityAlreadyExistsError) as exc_info:
            await use_case.execute(request)
        
        assert "уже существует" in str(exc_info.value)


class TestLoginUseCase:
    """Тесты для входа в систему"""

    @pytest.mark.asyncio
    async def test_login_success(self):
        """Успешный вход"""
        # Arrange
        user_id = uuid4()
        valid_hash = get_valid_password_hash("StrongP@ssw0rd")
        
        user = Mock(spec=UserEntity)
        user.id = user_id
        user.email = Email("test@example.com")
        user.full_name = "Test UserEntity"
        user.password_hash = PasswordHash(valid_hash)
        user.is_active = True
        user.get_all_permissions.return_value = {"global": ["user"]}
        user.roles = []
        user.update_last_login = Mock()

        mock_uow = AsyncMock()
        mock_uow.users.get_by_email = AsyncMock(return_value=user)
        mock_uow.users.update = AsyncMock()
        mock_uow.roles.get_by_user = AsyncMock(return_value=[])
        mock_uow.commit = AsyncMock()

        mock_password_hasher = Mock()
        mock_password_hasher.verify.return_value = True

        mock_token_service = Mock()
        mock_token_service.create_access_token.return_value = ("access_token", 3600)
        mock_token_service.create_refresh_token.return_value = ("refresh_token", 86400)

        mock_cache = AsyncMock()
        mock_cache.set_refresh_token = AsyncMock()
        mock_cache.set_user = AsyncMock()

        use_case = LoginUseCase(
            uow=mock_uow,
            password_hasher=mock_password_hasher,
            token_service=mock_token_service,
            cache=mock_cache
        )

        request = LoginRequestDTO(
            email="test@example.com",
            password="StrongP@ssw0rd"
        )

        # Act
        result = await use_case.execute(request)

        # Assert
        assert result.user_id == user_id
        assert result.email == "test@example.com"
        assert result.tokens.access_token == "access_token"
        assert result.tokens.refresh_token == "refresh_token"

        mock_uow.users.get_by_email.assert_called_once_with("test@example.com")
        mock_password_hasher.verify.assert_called_once()
        mock_uow.users.update.assert_called_once()
        mock_uow.commit.assert_called_once()
        mock_cache.set_refresh_token.assert_called_once()

    @pytest.mark.asyncio
    async def test_login_user_not_found(self):
        """Вход с несуществующим email"""
        # Arrange
        mock_uow = AsyncMock()
        mock_uow.users.get_by_email = AsyncMock(return_value=None)

        use_case = LoginUseCase(
            uow=mock_uow,
            password_hasher=Mock(),
            token_service=Mock(),
            cache=AsyncMock()
        )

        request = LoginRequestDTO(
            email="nonexistent@example.com",
            password="password"
        )

        # Act & Assert
        with pytest.raises(InvalidCredentialsError) as exc_info:
            await use_case.execute(request)
        
        assert "Неверный email или пароль" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_login_wrong_password(self):
        """Вход с неверным паролем"""
        # Arrange
        valid_hash = get_valid_password_hash("StrongP@ssw0rd")
        
        user = Mock(spec=UserEntity)
        user.password_hash = PasswordHash(valid_hash)
        user.is_active = True

        mock_uow = AsyncMock()
        mock_uow.users.get_by_email = AsyncMock(return_value=user)

        mock_password_hasher = Mock()
        mock_password_hasher.verify.return_value = False

        use_case = LoginUseCase(
            uow=mock_uow,
            password_hasher=mock_password_hasher,
            token_service=Mock(),
            cache=AsyncMock()
        )

        request = LoginRequestDTO(
            email="test@example.com",
            password="wrongpassword"
        )

        # Act & Assert
        with pytest.raises(InvalidCredentialsError) as exc_info:
            await use_case.execute(request)
        
        assert "Неверный email или пароль" in str(exc_info.value)


class TestVerifyEmailUseCase:
    """Тесты для подтверждения email"""

    @pytest.mark.asyncio
    async def test_verify_email_success(self):
        """Успешное подтверждение email"""
        # Arrange
        user_id = uuid4()
        email = "test@example.com"
        
        user = Mock(spec=UserEntity)
        user.id = user_id
        user.email = Email(email)
        user.verify_email = Mock()

        mock_uow = AsyncMock()
        mock_uow.users.get_by_id = AsyncMock(return_value=user)
        mock_uow.users.update = AsyncMock()
        mock_uow.commit = AsyncMock()

        mock_token_service = Mock()
        mock_token_service.verify_email_token.return_value = {
            "user_id": str(user_id),
            "email": email
        }

        mock_cache = AsyncMock()
        mock_cache.set_user = AsyncMock()

        use_case = VerifyEmailUseCase(
            uow=mock_uow,
            token_service=mock_token_service,
            cache=mock_cache
        )

        request = VerifyEmailRequestDTO(token="valid_token")

        # Act
        result = await use_case.execute(request)

        # Assert
        assert result.email == email
        assert "успешно" in result.message

        user.verify_email.assert_called_once()
        mock_uow.users.update.assert_called_once_with(user)
        mock_uow.commit.assert_called_once()
        mock_cache.set_user.assert_called_once_with(user)

    @pytest.mark.asyncio
    async def test_verify_email_invalid_token(self):
        """Подтверждение с неверным токеном"""
        # Arrange
        mock_token_service = Mock()
        mock_token_service.verify_email_token.return_value = None

        use_case = VerifyEmailUseCase(
            uow=AsyncMock(),
            token_service=mock_token_service,
            cache=AsyncMock()
        )

        request = VerifyEmailRequestDTO(token="invalid_token")

        # Act & Assert
        with pytest.raises(InvalidTokenError) as exc_info:
            await use_case.execute(request)
        
        assert "Неверный или истекший токен" in str(exc_info.value)


class TestResetPasswordUseCase:
    """Тесты для сброса пароля"""

    @pytest.mark.asyncio
    async def test_reset_password_success(self):
        """Успешный сброс пароля"""
        # Arrange
        user_id = uuid4()
        email = "test@example.com"
        valid_hash = get_valid_password_hash("NewStrongP@ssw0rd")
        
        user = Mock(spec=UserEntity)
        user.id = user_id
        user.email = Email(email)
        user.is_active = True
        user.password_hash = PasswordHash(valid_hash)
        user.updated_at = datetime.now(timezone.utc)

        mock_uow = AsyncMock()
        mock_uow.users.get_by_id = AsyncMock(return_value=user)
        mock_uow.users.update = AsyncMock()
        mock_uow.commit = AsyncMock()

        mock_password_hasher = Mock()
        mock_password_hasher.hash.return_value = valid_hash

        mock_token_service = Mock()
        mock_token_service.verify_password_reset_token.return_value = {
            "user_id": str(user_id),
            "email": email
        }

        mock_cache = AsyncMock()
        mock_cache.get_password_reset_token.return_value = "valid_token"
        mock_cache.delete_password_reset_token = AsyncMock()
        mock_cache.delete_refresh_token = AsyncMock()

        use_case = ResetPasswordUseCase(
            uow=mock_uow,
            password_hasher=mock_password_hasher,
            token_service=mock_token_service,
            cache=mock_cache
        )

        request = ResetPasswordRequestDTO(
            token="valid_token",
            new_password="NewStrongP@ssw0rd"
        )

        # Act
        result = await use_case.execute(request)

        # Assert
        assert "успешно" in result.message

        mock_uow.users.update.assert_called_once_with(user)
        mock_uow.commit.assert_called_once()
        mock_cache.delete_password_reset_token.assert_called_once_with(user_id)
        mock_cache.delete_refresh_token.assert_called_once_with(user_id)


class TestChangePasswordUseCase:
    """Тесты для изменения пароля"""

    @pytest.mark.asyncio
    async def test_change_password_success(self):
        """Успешное изменение пароля"""
        # Arrange
        user_id = uuid4()
        old_hash = get_valid_password_hash("OldP@ssw0rd")
        new_hash = get_valid_password_hash("NewStrongP@ssw0rd")
        
        user = Mock(spec=UserEntity)
        user.id = user_id
        user.password_hash = PasswordHash(old_hash)
        user.updated_at = datetime.now(timezone.utc)

        mock_uow = AsyncMock()
        mock_uow.users.get_by_id = AsyncMock(return_value=user)
        mock_uow.users.update = AsyncMock()
        mock_uow.commit = AsyncMock()

        mock_password_hasher = Mock()
        mock_password_hasher.verify.return_value = True
        mock_password_hasher.hash.return_value = new_hash

        mock_cache = AsyncMock()
        mock_cache.delete_refresh_token = AsyncMock()

        use_case = ChangePasswordUseCase(
            uow=mock_uow,
            password_hasher=mock_password_hasher,
            cache=mock_cache
        )

        request = ChangePasswordRequestDTO(
            current_password="OldP@ssw0rd",
            new_password="NewStrongP@ssw0rd"
        )

        # Act
        result = await use_case.execute(user_id, request)

        # Assert
        assert "успешно" in result.message

        mock_password_hasher.verify.assert_called_once_with("OldP@ssw0rd", old_hash)
        mock_uow.users.update.assert_called_once_with(user)
        mock_uow.commit.assert_called_once()
        mock_cache.delete_refresh_token.assert_called_once_with(user_id)


class TestRefreshTokenUseCase:
    """Тесты для обновления токена"""

    @pytest.mark.asyncio
    async def test_refresh_token_success(self):
        """Успешное обновление токена"""
        # Arrange
        user_id = uuid4()
        
        user = Mock(spec=UserEntity)
        user.id = user_id
        user.is_active = True
        user.get_all_permissions.return_value = {"global": ["user"]}

        mock_uow = AsyncMock()
        mock_uow.users.get_by_id = AsyncMock(return_value=user)
        mock_uow.roles.get_by_user = AsyncMock(return_value=[])

        mock_token_service = Mock()
        mock_token_service.verify_refresh_token.return_value = {
            "sub": str(user_id)
        }
        mock_token_service.create_access_token.return_value = ("new_access_token", 3600)

        mock_cache = AsyncMock()
        mock_cache.get_refresh_token.return_value = "valid_refresh_token"

        use_case = RefreshTokenUseCase(
            uow=mock_uow,
            token_service=mock_token_service,
            cache=mock_cache
        )

        request = RefreshTokenRequestDTO(refresh_token="valid_refresh_token")

        # Act
        result = await use_case.execute(request)

        # Assert
        assert result.access_token == "new_access_token"
        assert result.expires_in == 3600


class TestLogoutUseCase:
    """Тесты для выхода из системы"""

    @pytest.mark.asyncio
    async def test_logout_success(self):
        """Успешный выход"""
        # Arrange
        user_id = uuid4()
        
        mock_cache = AsyncMock()
        mock_cache.delete_refresh_token = AsyncMock()

        use_case = LogoutUseCase(cache=mock_cache)

        # Act
        await use_case.execute(user_id)

        # Assert
        mock_cache.delete_refresh_token.assert_called_once_with(user_id)