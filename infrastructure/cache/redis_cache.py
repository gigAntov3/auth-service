import json
from typing import Optional, Dict, Any, List
from uuid import UUID
from dataclasses import asdict
from datetime import datetime

from domain.entities.user import UserEntity

import redis.asyncio as redis
from datetime import timedelta

from domain.entities.role import Role, RoleType
from domain.value_objects.email import Email
from domain.value_objects.password import PasswordHash

from application.interfaces.cache_service import CacheService
from infrastructure.config import settings


class RedisCacheService(CacheService):
    """Реализация кэша на Redis"""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.user_prefix = "user:"
        self.refresh_token_prefix = "refresh_token:"
        self.password_reset_prefix = "password_reset:"
        self.invitation_prefix = "invitation:"
        self.default_ttl = settings.REDIS_DEFAULT_TTL

    # ========== UserEntity caching ==========

    async def get_user(self, user_id: UUID) -> Optional[UserEntity]:
        """Получить пользователя из кэша"""
        key = f"{self.user_prefix}{user_id}"
        data = await self.redis.get(key)
        if data:
            return self._user_from_dict(json.loads(data))
        return None

    async def set_user(self, user: UserEntity, ttl: int = None) -> None:
        """Сохранить пользователя в кэш"""
        key = f"{self.user_prefix}{user.id}"
        ttl = ttl or self.default_ttl
        await self.redis.setex(
            key, 
            ttl, 
            json.dumps(self._user_to_dict(user), default=str)
        )

    async def delete_user(self, user_id: UUID) -> None:
        """Удалить пользователя из кэша"""
        key = f"{self.user_prefix}{user_id}"
        await self.redis.delete(key)

    # ========== Refresh tokens ==========

    async def get_refresh_token(self, user_id: UUID) -> Optional[str]:
        """Получить refresh token пользователя"""
        key = f"{self.refresh_token_prefix}{user_id}"
        return await self.redis.get(key)

    async def set_refresh_token(self, user_id: UUID, token: str, ttl: int) -> None:
        """Сохранить refresh token"""
        key = f"{self.refresh_token_prefix}{user_id}"
        await self.redis.setex(key, ttl, token)

    async def delete_refresh_token(self, user_id: UUID) -> None:
        """Удалить refresh token"""
        key = f"{self.refresh_token_prefix}{user_id}"
        await self.redis.delete(key)

    # ========== Password reset tokens ==========

    async def get_password_reset_token(self, user_id: UUID) -> Optional[str]:
        """Получить токен сброса пароля"""
        key = f"{self.password_reset_prefix}{user_id}"
        return await self.redis.get(key)

    async def set_password_reset_token(self, user_id: UUID, token: str, ttl: int) -> None:
        """Сохранить токен сброса пароля"""
        key = f"{self.password_reset_prefix}{user_id}"
        await self.redis.setex(key, ttl, token)

    async def delete_password_reset_token(self, user_id: UUID) -> None:
        """Удалить токен сброса пароля"""
        key = f"{self.password_reset_prefix}{user_id}"
        await self.redis.delete(key)

    # ========== Invitations ==========

    async def get_invitation(self, invite_code: str) -> Optional[Dict]:
        """Получить данные приглашения"""
        key = f"{self.invitation_prefix}{invite_code}"
        data = await self.redis.get(key)
        return json.loads(data) if data else None

    async def set_invitation(self, invite_code: str, data: Dict, ttl: int = 604800) -> None:
        """Сохранить приглашение (7 дней по умолчанию)"""
        key = f"{self.invitation_prefix}{invite_code}"
        await self.redis.setex(key, ttl, json.dumps(data, default=str))

    async def delete_invitation(self, invite_code: str) -> None:
        """Удалить приглашение"""
        key = f"{self.invitation_prefix}{invite_code}"
        await self.redis.delete(key)

    # ========== Helper methods ==========

    def _user_to_dict(self, user: UserEntity) -> dict:
        """Конвертировать UserEntity в dict для JSON"""
        return {
            'id': str(user.id),
            'email': user.email.value,
            'full_name': user.full_name,
            'password_hash': user.password_hash.value,
            'is_active': user.is_active,
            'is_email_verified': user.is_email_verified,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'updated_at': user.updated_at.isoformat() if user.updated_at else None,
            'last_login_at': user.last_login_at.isoformat() if user.last_login_at else None,
            'roles': [
                {
                    'id': str(role.id),
                    'user_id': str(role.user_id),
                    'role_type': role.role_type.value,
                    'branch_id': str(role.branch_id) if role.branch_id else None,
                    'assigned_at': role.assigned_at.isoformat() if role.assigned_at else None,
                    'assigned_by': str(role.assigned_by) if role.assigned_by else None
                }
                for role in user.roles
            ]
        }

    def _user_from_dict(self, data: dict) -> UserEntity:
        """Конвертировать dict в UserEntity"""
        from domain.entities.user import UserEntity
        from domain.entities.role import Role
        
        user = UserEntity(
            id=UUID(data['id']),
            email=Email(data['email']),
            full_name=data['full_name'],
            password_hash=PasswordHash(data['password_hash']),
            is_active=data['is_active'],
            is_email_verified=data['is_email_verified'],
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None,
            last_login_at=datetime.fromisoformat(data['last_login_at']) if data.get('last_login_at') else None
        )
        
        # Загружаем роли
        for role_data in data.get('roles', []):
            role = Role(
                id=UUID(role_data['id']),
                user_id=UUID(role_data['user_id']),
                role_type=RoleType(role_data['role_type']),
                branch_id=UUID(role_data['branch_id']) if role_data.get('branch_id') else None,
                assigned_at=datetime.fromisoformat(role_data['assigned_at']) if role_data.get('assigned_at') else None,
                assigned_by=UUID(role_data['assigned_by']) if role_data.get('assigned_by') else None
            )
            user._roles.add(role)
        
        return user