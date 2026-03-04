import pytest
import json
from uuid import uuid4
from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock, patch

from infrastructure.cache.redis_cache import RedisCacheService
from domain.entities.user import UserEntity
from domain.entities.role import Role, RoleType
from domain.value_objects.email import Email
from domain.value_objects.password import PasswordHash

from tests.helpers import get_valid_password_hash


class TestRedisCacheService:
    """Тесты для Redis кэша"""

    @pytest.fixture
    def mock_redis(self):
        """Фикстура для мока Redis клиента"""
        redis = AsyncMock()
        redis.get = AsyncMock()
        redis.setex = AsyncMock()
        redis.delete = AsyncMock()
        return redis

    @pytest.fixture
    def cache_service(self, mock_redis):
        """Фикстура для сервиса кэша"""
        return RedisCacheService(mock_redis)

    @pytest.fixture
    def test_user(self):
        """Фикстура для тестового пользователя"""
        user_id = uuid4()
        user = UserEntity(
            id=user_id,
            email=Email("test@example.com"),
            full_name="Test UserEntity",
            password_hash=PasswordHash(get_valid_password_hash()),
            is_active=True,
            is_email_verified=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        # Добавляем роль
        role = Role(
            id=uuid4(),
            user_id=user_id,
            role_type=RoleType.USER,
            branch_id=None,
            assigned_at=datetime.now(timezone.utc),
            assigned_by=None
        )
        user._roles.add(role)
        
        return user

    @pytest.mark.asyncio
    async def test_set_user(self, cache_service, mock_redis, test_user):
        """Тест сохранения пользователя в кэш"""
        await cache_service.set_user(test_user, ttl=3600)
        
        mock_redis.setex.assert_called_once()
        args = mock_redis.setex.call_args[0]
        assert args[0] == f"user:{test_user.id}"
        assert args[1] == 3600
        
        # Проверяем, что данные сериализуются в JSON
        data = json.loads(args[2])
        assert data['id'] == str(test_user.id)
        assert data['email'] == test_user.email.value
        assert data['full_name'] == test_user.full_name
        assert len(data['roles']) == 1
        assert data['roles'][0]['role_type'] == RoleType.USER.value

    @pytest.mark.asyncio
    async def test_get_user_found(self, cache_service, mock_redis, test_user):
        """Тест получения пользователя из кэша (найден)"""
        # Подготавливаем данные
        user_data = {
            'id': str(test_user.id),
            'email': test_user.email.value,
            'full_name': test_user.full_name,
            'password_hash': test_user.password_hash.value,
            'is_active': test_user.is_active,
            'is_email_verified': test_user.is_email_verified,
            'created_at': test_user.created_at.isoformat(),
            'updated_at': test_user.updated_at.isoformat(),
            'last_login_at': None,
            'roles': [
                {
                    'id': str(role.id),
                    'user_id': str(role.user_id),
                    'role_type': role.role_type.value,
                    'branch_id': None,
                    'assigned_at': role.assigned_at.isoformat(),
                    'assigned_by': None
                }
                for role in test_user.roles
            ]
        }
        
        mock_redis.get.return_value = json.dumps(user_data)
        
        # Выполняем
        user = await cache_service.get_user(test_user.id)
        
        # Проверяем
        assert user is not None
        assert user.id == test_user.id
        assert user.email.value == test_user.email.value
        assert user.full_name == test_user.full_name
        assert len(user.roles) == 1
        assert list(user.roles)[0].role_type == RoleType.USER

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, cache_service, mock_redis):
        """Тест получения пользователя из кэша (не найден)"""
        user_id = uuid4()
        mock_redis.get.return_value = None
        
        user = await cache_service.get_user(user_id)
        
        assert user is None
        mock_redis.get.assert_called_once_with(f"user:{user_id}")

    @pytest.mark.asyncio
    async def test_delete_user(self, cache_service, mock_redis):
        """Тест удаления пользователя из кэша"""
        user_id = uuid4()
        
        await cache_service.delete_user(user_id)
        
        mock_redis.delete.assert_called_once_with(f"user:{user_id}")

    @pytest.mark.asyncio
    async def test_set_refresh_token(self, cache_service, mock_redis):
        """Тест сохранения refresh token"""
        user_id = uuid4()
        token = "refresh_token_123"
        ttl = 86400
        
        await cache_service.set_refresh_token(user_id, token, ttl)
        
        mock_redis.setex.assert_called_once_with(
            f"refresh_token:{user_id}",
            ttl,
            token
        )

    @pytest.mark.asyncio
    async def test_get_refresh_token(self, cache_service, mock_redis):
        """Тест получения refresh token"""
        user_id = uuid4()
        expected_token = "refresh_token_123"
        mock_redis.get.return_value = expected_token
        
        token = await cache_service.get_refresh_token(user_id)
        
        assert token == expected_token
        mock_redis.get.assert_called_once_with(f"refresh_token:{user_id}")

    @pytest.mark.asyncio
    async def test_delete_refresh_token(self, cache_service, mock_redis):
        """Тест удаления refresh token"""
        user_id = uuid4()
        
        await cache_service.delete_refresh_token(user_id)
        
        mock_redis.delete.assert_called_once_with(f"refresh_token:{user_id}")

    @pytest.mark.asyncio
    async def test_set_password_reset_token(self, cache_service, mock_redis):
        """Тест сохранения токена сброса пароля"""
        user_id = uuid4()
        token = "reset_token_123"
        ttl = 3600
        
        await cache_service.set_password_reset_token(user_id, token, ttl)
        
        mock_redis.setex.assert_called_once_with(
            f"password_reset:{user_id}",
            ttl,
            token
        )

    @pytest.mark.asyncio
    async def test_set_invitation(self, cache_service, mock_redis):
        """Тест сохранения приглашения"""
        invite_code = "INVITE123"
        data = {"user_id": str(uuid4()), "roles": ["manager"]}
        ttl = 604800
        
        await cache_service.set_invitation(invite_code, data, ttl)
        
        mock_redis.setex.assert_called_once()
        args = mock_redis.setex.call_args[0]
        assert args[0] == f"invitation:{invite_code}"
        assert args[1] == ttl
        assert json.loads(args[2]) == data